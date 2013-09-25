from .base import Module, extract_value


class User(Module):
    _name = 'user'

    @extract_value('users')
    def init(self):
        return self._request('init')


    def add(self):
    	#TODO vuln::download
        raise NotImplementedError


	def edit(self):
		#TODO vuln::download
        raise NotImplementedError


	def delete(self, *ids):
		"""Deletes user

		:param ids: list of user ids

		"return: returns response

		"""
		return self._request('delete',{
			'users': [{'id':id} for id in ids]
		} )


	def query(self, filters = None, start = None, sort = None, stop = None, 
				tool = None, password = None):
		"""Query Users module.

		:param filters: specified user filters
		:param start: startOffset
		:param sort: sortField
		:param stop: endOffset
		:param tool: query tool
		:param password: user password

		return: return params used
		"""

		return self._request('query', {
			'endOffset': end
			'startOffset': start
			'sortField': sort
			'tool': tool
			'password': password
			'filters': [{'id':id} for id in ids]
			})


	def changePassword(self,password):
		"""Change user's password

		:param password: user's specified password

		:return: returns response
		"""

		return self._request('password': password)


	def getCoverage(self, user):
		"""Get coverage for user.

		:param user: user's ID

		:return: returns user's coverage
		"""

		return self._request('userID': user)


	def validateAdd(self):[{'id':id} for id in ids]
		#TODO vuln::validateAdd
        raise NotImplementedError


	def validateEdit(self):
		#TODO vuln::validateEdit
        raise NotImplementedError


class Admin(User):
    _name = 'admin'

    #TODO? admin, might be duplicate of user
