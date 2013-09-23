from .base import Module, extract_value


class AttributeSets(Module):
    _name = "attribute_sets"

    def init(self):
        return self._request('init')

    def add(self):
        #TODO attribute::add
        raise NotImplementedError

    def edit(self):
        #TODO attribute::edit
        raise NotImplementedError

    def delete(self):
        #TODO attribute::delete
        raise NotImplementedError

    def validate_add(self):
        #TODO attribute::validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO attribute::validateEdit
        raise NotImplementedError