#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import MySQLdb

import telebot, time, os, logging
from telebot import types

db = MySQLdb.connect(host = 'localhost', user = 'root', db = 'buscq', charset = 'utf8')
cur = db.cursor()
logger = telebot.logger
bus_bot = telebot.TeleBot('') # your bot key goes here

telebot.logger.setLevel(logging.DEBUG)

time_ignore = 5 * 60

def get_nearest(latitude, longitude):
    query = """SELECT id, name, (
               6371000
               * acos(cos(radians(%(lat)s))
                  * cos(radians(lat))
                  * cos(radians(lon)
                  - radians(%(lon)s))
                  + sin(radians(%(lat)s))
                  * sin(radians(lat))
                )
               ) AS distance FROM `stops` ORDER BY distance LIMIT 10;
            """
# having distance < 5000
    data = {'lat': latitude, 'lon': longitude}
    cur.execute(query, data)
    if cur.rowcount == 0:
        return 'No se han encontrado paradas cercanas'
    elif cur.rowcount == 1:
        return get_bus(cur.fetchone()[0])
    else:
        output = 'Paradas más cercanas encontradas:\n\n'
        for(id, name, distance) in cur:
            output += 'ID: <b>' + str(id) + '</b>; <b>' + name.encode('utf-8') + '</b> (' + str(int(distance)) + ' metros)\n'
        return output

def get_bus(stop):
    stop_json = json.loads(requests.get('http://app.tussa.org/tussa/api/paradas/' + str(stop)).text)
    output = 'Próximos buses en <b>' + stop_json['nombre'].encode('utf-8') + '</b> (' + str(stop) + ')\n'
    if len(stop_json['lineas']) == 0:
        output += '\nNo hay buses disponibles para mostrar en este momento en esta parada\n'
    else:
        for i in stop_json['lineas']:
            output += 'Línea <b>' + i['sinoptico'].encode('utf-8') + '</b>: ' + str(i['minutosProximoPaso']) + ' minutos\n'
    output += '\nRecorrido de cada línea, horarios e información detallada en https://buscq.com/parada/' + str(stop)
    return output

@bus_bot.message_handler(commands=['start'])
def handle_start_help(m):
    if (int(time.time()) - time_ignore) > m.date:
        return

    bus_bot.send_chat_action(m.chat.id, 'typing')
    markup = types.ReplyKeyboardMarkup()
    itembtn1 = types.KeyboardButton('/parada')
    markup.row(itembtn1)

    bus_bot.send_message(m.chat.id, 'Por favor, elige una acción', reply_markup = markup)

@bus_bot.message_handler(commands=['parada'])
def get_id(m):
    if (int(time.time()) - time_ignore) > m.date:
        return

    a = m.text.lower().replace('avenida', 'avda').split()
    output = ''
    if len(a) > 1:
        if a[1].isdigit():
            output = get_bus(a[1])
        else:
            query = ('SELECT id, name FROM `stops` WHERE name LIKE %(name)s LIMIT 10')
            cur.execute(query, {'name': '%' + '%'.join(a[1:len(a)]) + '%'})
            if cur.rowcount == 0:
                output = 'No se han encontrado paradas con ese nombre'
            elif cur.rowcount == 1:
                output = get_bus(cur.fetchone()[0])
            else:
                output = 'Varias paradas encontradas:\n\n'
                for(id, name) in cur:
                    output += 'ID: <b>' + str(id) + '</b>; <b>' + name + '</b>\n'
    else:
        output = 'Error de argumento. Uso: /parada <i>parada</i>. Puedes encontrar todas las paradas en https://buscq.com.\nTambién puedes enviar tu ubicación para ver una lista de paradas más cercanas.'

    bus_bot.send_message(m.chat.id, output, parse_mode='HTML')

@bus_bot.message_handler(content_types=['location'])
def handle_location(m):
    bus_bot.send_message(m.chat.id, get_nearest(m.location.latitude, m.location.longitude), parse_mode='HTML')

bus_bot.polling(none_stop = True)
