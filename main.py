import asyncio
import aiohttp
import datetime
from typing import List
from config import MAX_REQUESTS
from more_itertools import chunked
from models import Session_db, InfoSwPerson, open_conn_db, close_conn_db


def connection_client(method):
    async def wrapper(*args, **kwargs):
        async with aiohttp.ClientSession() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                raise e
            finally:
                await session.close()

    return wrapper



@connection_client
async def get_count_person(session: aiohttp.ClientSession):  # Получаем кол-во записей в API
    response = await session.get('https://swapi.dev/api/people/')
    json = await response.json()
    return json['count']


@connection_client
async def get_list(
    json_persons: List[dict],
    key: str,
    field_name: str,
    session: aiohttp.ClientSession
):
    for person in json_persons:
        names = []
        list_url = person.get(key)
        if list_url is None:
            continue
        for item in list_url:
            response = await session.get(item)
            json_data = await response.json()
            names.append(json_data[field_name])
        person[key] = ', '.join(names)

    return json_persons


@connection_client
async def get_info_character(id: int, session: aiohttp.ClientSession):
    response = await session.get(f'https://swapi.dev/api/people/{id}/')
    json_data = await response.json()
    return json_data


async def create_person_db(result_json_person: List[dict]):
    async with Session_db() as session:
        for person in result_json_person:
            person = InfoSwPerson(
                birth_year = person.get('birth_year' , 'unknown'),
                eye_color = person.get('eye_color' , 'unknown'),
                films = person.get('films' , 'unknown'),
                gender = person.get('gender' , 'unknown'),
                hair_color = person.get('hair_color' , 'unknown'),
                height = person.get('height' , 'unknown'),
                homeworld = person.get('homeworld' , 'unknown'),
                mass = person.get('mass' , 'unknown'),
                name = person.get('name' , 'unknown'),
                skin_color = person.get('skin_color' , 'unknown'),
                species = person.get('species' , 'unknown'),
                starships = person.get('starships' , 'unknown'),
                vehicles = person.get('vehicles' , 'unknown')
            )
            session.add(person)
        await session.commit()


async def main():
    await open_conn_db()
    count_request = await get_count_person()
    for list_person_id in chunked(range(1, count_request + 1), MAX_REQUESTS):
        coros = [get_info_character(id) for id in list_person_id]
        result_coros = await asyncio.gather(*coros)
        curent_films_persons =  await get_list(result_coros, 'films', 'title')
        curent_starships_persons = await get_list(curent_films_persons, 'starships', 'name')
        curent_vehicles_persons = await get_list(curent_starships_persons, 'vehicles', 'name')
        curent_species_persons = await get_list(curent_vehicles_persons, 'species', 'name')

        insert_task = asyncio.create_task(create_person_db(curent_species_persons))
    
    tasks = asyncio.all_tasks()
    current_task = asyncio.current_task()
    tasks.remove(current_task)
    await asyncio.gather(*tasks)
    await close_conn_db()
        
        

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)