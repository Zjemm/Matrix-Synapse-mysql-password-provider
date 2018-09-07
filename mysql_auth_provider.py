# -*- coding: utf-8 -*-
#
# mysql Authentication module for Matrix synapse
# Copyright (C) 2018 Eelke Smit
# https://sjemm.net
#
# Based on juju2143/matrix-synapse-smf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__version__ = "0.1.1"

from twisted.internet import defer
import logging
import bcrypt
from mysql.connector import MySQLConnection, Error


logger = logging.getLogger(__name__)

class MysqlAuthProvider(object):
	__version__ = "0.1.1"

	def __init__(self, config, account_handler):
		self.account_handler = account_handler
		self.mysql_host = config.host
		self.mysql_user = config.user
		self.mysql_password = config.password
		self.mysql_database = config.database

	@defer.inlineCallbacks
	def check_password(self, user_id, password):
		if not password:
			defer.returnValue(False)

		localpart = user_id.split(":", 1)[0][1:]
		conn = MySQLConnection(user=self.mysql_user, password=self.mysql_password, host=self.mysql_host, database=self.mysql_database)
		cursor = conn.cursor()
        sql = "SELECT password FROM virtual_users WHERE email = %s"
        user_email = (localpart, )

		cursor.execute(sql, user_email)
		hash = cursor.fetchone()

		if not hash:
			defer.returnValue(False)

		if bcrypt.checkpw(password.encode('utf-8'), hash[0].encode('utf-8')):
			logger.info("Valid password for user %s: %s", localpart, hash[0])
			if (yield self.account_handler.check_user_exists(user_id)):
				logger.info("User %s exists, logging in", user_id)
				defer.returnValue(True)
			else:
				try:
					user_id, access_token = (
						yield self.account_handler.register(localpart=localpart)
					)
					logger.info("User %s created, logging in", localpart)
					defer.returnValue(True)
				except:
					logger.warning("User %s not created", localpart)
					defer.returnValue(False)
		else:
			logger.warning("Wrong password for user %s", localpart)
			defer.returnValue(False)

	@staticmethod
	def parse_config(config):
		class _MysqlConfig(object):
			pass
		mysql_config = _MysqlConfig()
		mysql_config.enabled = config.get("enabled", False)
		mysql_config.host = config.get("host", "localhost")
		mysql_config.user = config.get("user", "mailuser")
		mysql_config.password = config.get("password", "")
		mysql_config.database = config.get("database", "virtual_users")

		return mysql_config

	def cleanup(self):
		self.db.close()
