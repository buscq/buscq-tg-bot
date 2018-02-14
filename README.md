# buscq.com Telegram bot
Real-time data from Santiago de Compostela buses, in a Telegram bot

There's just one command, `/parada`, which accepts a stop ID or name as an argument. Examples:

`/parada 536`
`/parada virxe da cerca`
`/parada rosalía`

If more than a stop is found, a disambiguation message will be shown.

Also, if location is sent, a list of nearest stops will be returned (10 stops max)

### Required libraries

* [telebot](https://github.com/eternnoir/pyTelegramBotAPI)

### Usage notes

Replace the Telegram bot key in [buscq_bot.py](buscq_bot.py)

For the location functionality, the use of MySQL or MariaDB is required. Table structure and data are available [here](table.sql).

### Contributors
 *  [@ResonantWave](https://github.com/ResonantWave)

### Contributing
 *  The code is licensed under the [GPL v3.0](LICENSE)
 *  Feel free to contribute to the code

### Acknowledgements
 * Thanks to [Tussa](http://tussa.org) for the bus data

