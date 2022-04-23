# -*- coding: utf-8 -*-
# Marusya - VK Api
import json
import logging
from io import BytesIO
from typing import Optional

import requests


log = logging.getLogger('vk_api')


class VKApi:
    '''Обработчик запросов к VK Api.

        Args:
            token (str): VK Api токен.
    '''
    def __init__(self, token: str) -> None:
        self._base_endpoint = 'https://api.vk.com/method/'
        self._default_params = {'access_token': token, 'v': '5.131'}
        self._default_params_str = f'&access_token={token}&v=5.131'
        self._token = token

    def _make_request(self, method: str, endpoint: str, args: dict = {}, body: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
        '''Выполнит запрос к VK Api.

        Args:
            method (str): HTTP метод.
            endpoint (str): VK API endpoint. aka "method".
            args (dict): Дополнительные аргументы в dict формате. Defaults is {}.
            body (Optional[dict]): Тело запроса. Defaults is None.
            headers (Optional[dict]): Заголовки запроса. Defaults is None.

        Returns:
            dict: Ответ VK Api.
        '''
        log.debug(f'Called with args ({method}, {endpoint}, {args}, {body})')
        url = self._base_endpoint + endpoint
        params = self._default_params
        params.update(args)
        log.debug(f'Params: {params}')
        if body:
            if headers:
                resp = requests.request(method, url, data=json.dumps(body), headers=headers, params=params)
            else:
                resp = requests.request(method, url, data=json.dumps(body), params=params)
            log.debug(f'Response: {resp.text}')
            if resp.ok:
                return resp.json()
            else:
                log.error(f'Request error {resp.status_code} on "{url}" with body "{body}": {resp.text}')
                return {}
        else:
            if headers:
                resp = requests.request(method, url, headers=headers, params=params)
            else:
                resp = requests.request(method, url, params=params)
            log.debug(f'Response: {resp.text}')
            if resp.ok:
                return resp.json()
            else:
                log.error(f'Request error {resp.status_code} on "{url}": {resp.text}')
                return {}

    def marusia_getPictureUploadLink(self) -> dict:
        '''Возвращает URL для загрузки изображения.

        Returns:
            dict: VK Api result.
        '''
        resp = self._make_request('GET', 'marusia.getPictureUploadLink', headers={'Content-Length': '0'})
        return resp

    def marusia_uploadPicture(self, url: str, file: BytesIO) -> dict:
        '''Загрузить фотографию на сервер VK.

        Args:
            url (str): VK Api upload link.
            file (BytesIO): File in BytesIO.

        Returns:
            dict: VK Api reqsponse.
        '''
        log.debug('Called!')
        url += self._default_params_str
        resp = requests.request('POST', url, files={'photo': file})
        if resp.ok:
            log.debug(f'File successfull uploaded: {resp.text}')
            return resp.json()
        else:
            log.error(f'Upload error {resp.status_code}: {resp.text}')
            return {}

    def marusia_savePicture(self, server: int, hash: str, photo: dict) -> dict:
        '''Сохраняет фотографию в скиле.

        Args:
            server (int): uploadPicture server result.
            hash (str): uploadPicture hash result.
            photo (dict): uploadPicture photo result.

        Returns:
            dict: VK Api result.
        '''
        log.debug(f'Called with args ({server}, {hash}, {photo})')
        params = {
            'server': str(server),
            'hash': hash,
            'photo': json.dumps(photo, separators=(',', ':'))
        }
        resp = self._make_request('GET', 'marusia.savePicture', args=params)
        return resp

    def marusia_getPictures(self) -> dict:
        '''Возвращает список доступных фотографий.

        Returns:
            dict: VK Api result.
        '''
        log.debug('Called!')
        return self._make_request('GET', 'marusia.getPictures')

    def marusia_deletePicture(self, id: int) -> dict:
        '''Удаляет фотографию из навыка.

        Args:
            id (int): VK Api photo id.

        Returns:
            dict: VK Api result.
        '''
        log.debug(f'Called with args ({id})')
        return self._make_request('GET', 'marusia.deletePicture', {'id': id})

    def uploadPicture(self, file: BytesIO) -> Optional[int]:
        '''Загружает фотографию в навык и возвращает её id.

        Args:
            file (BytesIO): Picture file.

        Returns:
            Optional[int]: VK Api picture id. If successfull.
        '''
        link = self.marusia_getPictureUploadLink()
        if link:
            ph = self.marusia_uploadPicture(link['response']['picture_upload_link'], file)
            if ph:
                pic = self.marusia_savePicture(ph['server'], ph['hash'], ph['photo'])
                if pic:
                    return pic['response']['photo_id']
        return None
