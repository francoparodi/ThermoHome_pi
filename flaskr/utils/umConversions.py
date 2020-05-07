def celsiusToFahrenheit(temp, decimals):
    return round( ((temp * 9/5) + 32), decimals) 

def fahrenheitToCelsius(temp, decimals):
    return round( ((temp - 32) * 5/9), decimals)