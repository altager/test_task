import logging
import ujson as json

logger = logging.getLogger(__name__)


class SongsDAO:
    def __init__(self, mongo_connection, cache_backend):
        self._mongo_connection = mongo_connection
        self._cache_backend = cache_backend

    def get_songs_list(self, limit=None, last_id=None):
        if last_id:
            songs_list = self._mongo_connection.songs.aggregate(
                [
                    {'$match': {'_id': {'$gt': last_id}}},
                    {'$project': {'_id': 0, 'id': {'$toString': '$_id'}, 'artist': 1, 'title': 1, 'difficulty': 1,
                                  'level': 1, 'released': 1}},
                    {'$limit': limit}
                ]
            )
        else:
            songs_list = self._mongo_connection.songs.aggregate(
                [
                    {'$project': {'_id': 0, 'id': {'$toString': '$_id'}, 'artist': 1, 'title': 1, 'difficulty': 1,
                                  'level': 1, 'released': 1}},
                    {'$limit': limit}
                ]
            )

        return list(songs_list)

    def get_average_difficulty(self, level=None):
        result = self._get_average_difficulty_from_cache(level=level)
        if not result:
            if level:
                result = list(self._get_average_difficulty_from_db(level=level))[0]
                self._cache_backend.upsert_value(
                    f'average_difficulty_{level}', value=json.dumps(result), expire_in=60
                )
            else:
                result = list(self._get_average_difficulty_from_db())[0]
                self._cache_backend.upsert_value(
                    'average_difficulty_all', value=json.dumps(result), expire_in=60
                )

        return result

    def _get_average_difficulty_from_db(self, level=None):
        if level:
            result = self._mongo_connection.songs.aggregate(
                [
                    {'$match': {'level': level}},
                    {'$group': {'_id': None, 'average_difficulty': {'$avg': '$difficulty'}}},
                    {'$project': {'_id': 0, 'level': {'$literal': level}, 'average_difficulty': 1}}
                ]
            )

        else:
            result = self._mongo_connection.songs.aggregate(
                [
                    {'$group': {'_id': None, 'average_difficulty': {'$avg': '$difficulty'}}},
                    {'$project': {'_id': 0, 'level': 'all', 'average_difficulty': 1}}
                ]
            )
        return result

    def _get_average_difficulty_from_cache(self, level=None):
        if level:
            cached_value = self._cache_backend.get_value(f'average_difficulty_{level}')
        else:
            cached_value = self._cache_backend.get_value(f'average_difficulty_all')

        return cached_value
