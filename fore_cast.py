import sys
sys.path.append('..')
import dbQuery as db

class fore_cast:
    def __init__(self, date):
        self.chi_weight = .5
        self.date = date

    def create_forecast_dict(self):
        """creates forecast by zip and sku"""
        fore_cast = self.generate_forecast(self.date)
        self.fore_cast = {}
        for i in fore_cast:
            if i[1] not in self.fore_cast:
                self.fore_cast[i[1]] = {}
            self.fore_cast[i[1]][i[0]] = i[2]
        return self.fore_cast

    @staticmethod
    def generate_forecast(date):
        forecast = db.getDataFromString("exec [forecast] '" + str(date) + "', 365")
        return forecast

