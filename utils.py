from datetime import datetime


def logfile(directory):
    file = open(f'{directory}\\logfile.txt', 'a')

    def log(message):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        file.write(f"{now} : {message}\n")

    return log
