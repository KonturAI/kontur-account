import io
import asyncio
from typing import Optional, Tuple
from dataclasses import dataclass

import aiohttp
from aiohttp import ClientSession

from internal import interface, model


class AsyncWeed(interface.IStorage):
    def __init__(self, weed_master_host: str, weed_master_port: int, timeout: int = 30):
        self.master_url = f"http://{weed_master_host}:{weed_master_port}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """Получить или создать HTTP сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def _assign_file_key(self) -> dict:
        """Получить ключ для загрузки файла"""
        session = await self._get_session()

        async with session.get(f"{self.master_url}/dir/assign") as response:
            if response.status != 200:
                raise Exception(f"Failed to assign file key: {response.status}")
            return await response.json()

    async def _lookup_volume(self, volume_id: str) -> dict:
        """Найти volume по ID"""
        session = await self._get_session()

        async with session.get(f"{self.master_url}/dir/lookup", params={"volumeId": volume_id}) as response:
            if response.status != 200:
                raise Exception(f"Failed to lookup volume: {response.status}")
            return await response.json()

    def _parse_fid(self, fid: str) -> Tuple[str, str]:
        """Разобрать FID на volume_id и file_key"""
        if ',' not in fid:
            raise ValueError(f"Invalid FID format: {fid}")
        volume_id, file_key = fid.split(',', 1)
        return volume_id, file_key

    async def upload(self, file: io.BytesIO, name: str) -> model.AsyncWeedOperationResponse:
        """Загрузить файл в SeaweedFS"""
        try:
            # Получаем ключ для загрузки
            assign_result = await self._assign_file_key()
            fid = assign_result['fid']
            upload_url = f"http://{assign_result['url']}/{fid}"

            # Подготавливаем данные для загрузки
            file.seek(0)
            file_data = file.read()

            session = await self._get_session()

            # Создаем form data
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename=name)

            # Загружаем файл
            async with session.post(upload_url, data=data) as response:
                content = await response.read()

                if response.status not in [200, 201]:
                    raise Exception(f"Upload failed: {response.status}, {content.decode()}")

                return model.AsyncWeedOperationResponse(
                    status_code=response.status,
                    content=content,
                    content_type=response.headers.get('Content-Type', ''),
                    headers=dict(response.headers),
                    fid=fid,
                    url=upload_url,
                    size=len(file_data)
                )

        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    async def download(self, fid: str, name: str) -> tuple[io.BytesIO, str]:
        try:
            volume_id, file_key = self._parse_fid(fid)

            # Находим volume
            lookup_result = await self._lookup_volume(volume_id)
            if 'locations' not in lookup_result or not lookup_result['locations']:
                raise Exception(f"Volume {volume_id} not found")

            volume_server = lookup_result['locations'][0]['url']
            download_url = f"http://{volume_server}/{fid}"

            if name:
                download_url += f"?filename={name}"

            session = await self._get_session()

            # Скачиваем файл
            async with session.get(download_url) as response:
                if response.status != 200:
                    raise Exception(f"Download failed: {response.status}")

                content = await response.read()
                content_type = response.headers.get('Content-Type', 'application/octet-stream')

                file_obj = io.BytesIO(content)
                return file_obj, content_type

        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")

    async def delete(self, fid: str, name: str) -> model.AsyncWeedOperationResponse:
        try:
            volume_id, file_key = self._parse_fid(fid)

            # Находим volume
            lookup_result = await self._lookup_volume(volume_id)
            if 'locations' not in lookup_result or not lookup_result['locations']:
                raise Exception(f"Volume {volume_id} not found")

            volume_server = lookup_result['locations'][0]['url']
            delete_url = f"http://{volume_server}/{fid}"

            if name:
                delete_url += f"?filename={name}"

            session = await self._get_session()

            # Удаляем файл
            async with session.delete(delete_url) as response:
                content = await response.read()

                if response.status not in [200, 202, 204]:
                    raise Exception(f"Delete failed: {response.status}, {content.decode()}")

                return model.AsyncWeedOperationResponse(
                    status_code=response.status,
                    content=content,
                    content_type=response.headers.get('Content-Type', ''),
                    headers=dict(response.headers),
                    fid=fid
                )

        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    async def update(self, file: io.BytesIO, fid: str, name: str) -> model.AsyncWeedOperationResponse:
        """Обновить файл в SeaweedFS"""
        try:
            volume_id, file_key = self._parse_fid(fid)

            # Находим volume
            lookup_result = await self._lookup_volume(volume_id)
            if 'locations' not in lookup_result or not lookup_result['locations']:
                raise Exception(f"Volume {volume_id} not found")

            volume_server = lookup_result['locations'][0]['url']
            update_url = f"http://{volume_server}/{fid}"

            # Подготавливаем данные для обновления
            file.seek(0)
            file_data = file.read()

            session = await self._get_session()

            # Создаем form data
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename=name)

            # Обновляем файл
            async with session.put(update_url, data=data) as response:
                content = await response.read()

                if response.status not in [200, 201]:
                    raise Exception(f"Update failed: {response.status}, {content.decode()}")

                return model.AsyncWeedOperationResponse(
                    status_code=response.status,
                    content=content,
                    content_type=response.headers.get('Content-Type', ''),
                    headers=dict(response.headers),
                    fid=fid,
                    url=update_url,
                    size=len(file_data)
                )

        except Exception as e:
            raise Exception(f"Failed to update file: {str(e)}")

    async def get_cluster_status(self) -> dict:
        """Получить статус кластера SeaweedFS"""
        session = await self._get_session()

        async with session.get(f"{self.master_url}/cluster/status") as response:
            if response.status != 200:
                raise Exception(f"Failed to get cluster status: {response.status}")
            return await response.json()

    async def get_volume_status(self, volume_id: str) -> dict:
        """Получить статус конкретного volume"""
        lookup_result = await self._lookup_volume(volume_id)
        return lookup_result

    async def close(self):
        """Закрыть HTTP сессию"""
        if self._session and not self._session.closed:
            await self._session.close()

    def __del__(self):
        """Деструктор для автоматического закрытия сессии"""
        if hasattr(self, '_session') and self._session and not self._session.closed:
            # Создаем задачу для закрытия сессии в event loop, если он существует
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._session.close())
                else:
                    loop.run_until_complete(self._session.close())
            except RuntimeError:
                # Event loop не найден или не запущен
                pass

