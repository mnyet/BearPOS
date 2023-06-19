
# BearPOS

A python based POS System with Python and MySQL. This is my very first major Python Project that is fully functional and portable enough for easy installation. This is supposed to be my project submission for our 'Integrating Programming Technologies 2' (IPTC312).

The project is still barebones, but functional enough to do the most basic POS things.


## Features

- Cashier Management System.
- Inventory Management System.
- Order History for Past Orders.
- Cross platform for Both Linux and Windows Operating Systems.


## Installation

To install BearPOS, you need Python 3.11+ installed, along with XAMPP or any MySQL database you want to use.

You need to install mysql-connector and pyqt5 as these dependencies are necessary for the program to work.

**Install MySQL Connector (Install thru PiP).**
```python
  pip install mysql-connector-python
```

**Install PyQT5 (Also in PiP).**
```python
  pip install pyqt5
```

After both dependencies are installed, you can now start the program by going to the folder of the program and just run the program with Python **(Windows)**.

In **Linux**, you can just open the terminal and type
```python
  python3 main.py
```

And the program should start as intended. If the program closes by itself, meaning you still haven't started your MySQL service or you didn't install the libraries needed yet. So make sure all of these three are set up before starting up the program.