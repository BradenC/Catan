class CatanError(Exception):
    pass


class BuyError(CatanError):
    pass


class InputError(CatanError):
    pass


class PlaceError(CatanError):
    pass


class TurnError(CatanError):
    pass
