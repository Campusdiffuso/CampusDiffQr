from campusdiffuso import create_app
from campusdiffuso.users.utils import check_date_of_expiration
import multiprocessing

app = create_app()

if __name__ == "__main__":
   app.run()

   loop_process = multiprocessing.Process(target=check_date_of_expiration)
   loop_process.start()
