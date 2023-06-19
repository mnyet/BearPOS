from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
import sys, time, mysql.connector as mysql, string, random, datetime, webbrowser


cashierHandler = ""

#where connections initialize

mydb = mysql.connect(
    host = "localhost",
    user = "root",
    password = ""
    )
mycursor = mydb.cursor()

def prepareData():
    mycursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'db_BearPOS'")
    if mycursor.fetchone() == None:
        print("Database doesn't exist, going to prepare all the data...")
        #queries for preparing the database and table
        mycursor.execute("CREATE DATABASE db_BearPOS") #creates the database from the main cursor
        
        mydb_database = mysql.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "db_BearPOS"
            )

        createTableCursor = mydb_database.cursor()

        #uses the connection with database forda creation of tables
        createTableCursor.execute("""CREATE TABLE tbl_productList(id int primary key AUTO_INCREMENT,
                         productID varchar(60),
                         productName varchar(100),
                         price varchar(60));""")
        createTableCursor.execute("""CREATE TABLE tbl_orderHistory(order_id varchar(10) primary key,
                         orderDate varchar(60),
                         totalPrice varchar(100),
                         cashierOnSession varchar(60));""")
        createTableCursor.execute("""CREATE TABLE tbl_orderContents(order_id varchar(10),
                         productID varchar(60),
                         orderQty varchar(10),
                         productName varchar(100),
                         price varchar(60),
                         orderPrice varchar(60));""")
        createTableCursor.execute("""CREATE TABLE tbl_cashierList(id int primary key AUTO_INCREMENT,
                         cashierName varchar(60),
                         registrationDate varchar(60),
                         cashierPassword varchar(60));""")
        createTableCursor.execute("""INSERT INTO tbl_cashierList(cashierName, registrationDate, cashierPassword) VALUES ('user0', 'day of the lord' , md5('12345'))""")

        #finalize the insert queries
        mydb_database.commit()
        createTableCursor.close()                          
        
        time.sleep(3)
        print("Done.")
        time.sleep(2)
        
    else:
        print("Database already exists.")
        #time.sleep(1.5)

prepareData()

#pagtapos ng pagcheck ng database

try:
    con = mysql.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "db_BearPOS")

    if con:
        print("Hi")
        

except Exception as e:
    e = input("No connection, press enter to exit...")
    exit()

print("Connected to " + str(con))

#cursor for database
dbcursor = con.cursor()

#classes of every window

class loginScreen(QMainWindow):
	def __init__(self):

		self.openOtherWindow = False
		self.isYes = True

		super(loginScreen, self).__init__()

		#load the ui file
		uic.loadUi('login.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

		#widget define
			#entry
		self.entryUsername = self.findChild(QLineEdit, "entryUsername")
		self.entryPassword = self.findChild(QLineEdit, "entryPassword")

			#buttons
		self.btnLogin = self.findChild(QPushButton, "loginButton")
		self.btnLogin.clicked.connect(self.loginAttempt)

		self.btnAboutDev = self.findChild(QPushButton, "aboutDevButton")
		self.btnAboutDev.clicked.connect(self.openAboutDev)

	def loginAttempt(self):

		self.query = "SELECT cashierName, cashierPassword FROM tbl_cashierlist WHERE cashierName = '" + self.entryUsername.text() +"' AND cashierPassword = md5('" + self.entryPassword.text() +"')"
		dbcursor.execute(self.query)

		self.res = dbcursor.fetchone()

		if self.res:
			self.err = QMessageBox.information(self, 'Login Successful', 'Welcome back, ' + self.entryUsername.text(),
				QMessageBox.Ok)
			self.close()
			global cashierHandler
			cashierHandler = self.entryUsername.text()
			self.startSession = MainPOS()
			self.startSession.show()
		else:
			self.err = QMessageBox.critical(self, 'Incorrect Credentials', 'Please enter the correct username and password.',
				QMessageBox.Ok)
			
	def openAboutDev(self):
		self.startAboutDev = aboutDev()
		self.startAboutDev.show()

class aboutDev(QMainWindow):
	def __init__(self):
		super(aboutDev, self).__init__()

		#load the ui file
		uic.loadUi('aboutDev.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

#  _____   ____   _____    _____ ____  _____  ______  _____ 
# |  __ \ / __ \ / ____|  / ____/ __ \|  __ \|  ____|/ ____|
# | |__) | |  | | (___   | |   | |  | | |  | | |__  | (___  
# |  ___/| |  | |\___ \  | |   | |  | | |  | |  __|  \___ \ 
# | |    | |__| |____) | | |___| |__| | |__| | |____ ____) |
# |_|     \____/|_____/   \_____\____/|_____/|______|_____/ 
                                                           
                                                           

class MainPOS(QMainWindow):

	def closeEvent(self, event):
		if self.openOtherWindow:
			reply = QMessageBox.question(self, 'You are about to end the session', 'Are you sure you want to close this session?',
			QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

			if reply == QMessageBox.Yes:
				print('Window closed')
				self.isYes = True
			else:
				self.isYes = False
				event.ignore()
		else:
			reply = QMessageBox.question(self, 'You are about to close the program', 'Are you sure you want to close the program?',
			QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

			if reply == QMessageBox.Yes:
				print('Window closed')
				sys.exit()
			else:
				self.isYes = False
				event.ignore()

	def __init__(self):

		self.openOtherWindow = False
		self.isYes = True

		super(MainPOS, self).__init__()

		#load the ui file
		uic.loadUi('base.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

		#widget define
			#label texts
		self.lblCashierLabel = self.findChild(QLabel, "cashierLabel")
		self.lblGreetingLabel = self.findChild(QLabel, "greetingLabel")
		self.lblTotalPriceLabel = self.findChild(QLabel, "totalPriceLabel")

		self.lblCashierLabel.setText("Cashier: " + cashierHandler)

			#tables
		self.orderList = self.findChild(QTableWidget, "tblOrderList")
		self.orderList.setColumnWidth(0, 100)
		self.orderList.setColumnWidth(1, 50)
		self.orderList.setColumnWidth(2, 389)
		self.orderList.setColumnWidth(3, 50)
		self.orderList.setColumnWidth(4, 50)
		self.orderList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.orderList.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

			#entry
		self.entryProductID = self.findChild(QLineEdit, "productID")
		self.entryQuantity = self.findChild(QLineEdit, "quantity")

			#buttons
		self.btnEnterProductID = self.findChild(QPushButton, "addProductToList")
		self.btnNextCustomer = self.findChild(QPushButton, "nextCustomer")
		self.btnOrderHistory = self.findChild(QPushButton, "orderHistory")
		self.btnProductListing = self.findChild(QPushButton, "productListing")

		#adding/connecting function to buttons
		self.btnNextCustomer.clicked.connect(self.submitOrderNow)
		self.btnEnterProductID.clicked.connect(self.enterProductIDNow)
		self.btnOrderHistory.clicked.connect(self.orderHistoryNow)
		self.btnProductListing.clicked.connect(self.productListingNow)

		#show the ui
		#self.show()

	def id_generator(self, size=8, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def enterProductIDNow(self):
		try:

			#self.check_table_entry_exists(self.orderList, self.entryProductID.text().upper())

			if len(self.entryProductID.text()) == 0 or len(self.entryQuantity.text()) == 0:
				self.err = QMessageBox.critical(self, 'Incomplete Fields', 'Please fill all the fields.',
				QMessageBox.Ok)
			else:
				print(self.entryProductID.text())
				print(self.entryQuantity.text())
				prodQuantity = int(self.entryQuantity.text())

				self.query = "SELECT * FROM `tbl_productlist` WHERE `productID` = '" + self.entryProductID.text().upper() +"'"
				dbcursor.execute(self.query)

				self.res = dbcursor.fetchone()

				if self.res:
					print("Product Found")
					#print(self.res)
					
					self.listProdID = self.res[1]
					self.listQty = prodQuantity
					self.listProdName = self.res[2]
					self.listPrice = self.res[3]
					self.listTotal = int(self.listPrice) * self.listQty

					rowCount = self.orderList.rowCount()
					#row = 0
					#print("Rows: " + str(rowCount))

					if rowCount == 0:
						if self.listProdID and self.listQty and self.listProdName and self.listPrice and self.listTotal is not None:
							self.orderList.insertRow(rowCount)

							self.orderList.setItem(rowCount, 0, QTableWidgetItem(str(self.listProdID)))
							self.orderList.setItem(rowCount, 1, QTableWidgetItem(str(self.listQty)))
							self.orderList.setItem(rowCount, 2, QTableWidgetItem(str(self.listProdName)))
							self.orderList.setItem(rowCount, 3, QTableWidgetItem(str(self.listPrice)))
							self.orderList.setItem(rowCount, 4, QTableWidgetItem(str(self.listTotal)))

					else:
						for row in range(self.orderList.rowCount()):
							#print(item.text())
							if self.orderList.item(row, 0).text() == self.entryProductID.text().upper():
								#print("Product Exists.")
								isListed = True
								#print(self.orderList.item(row, 0).text())
								break
							else:
								#print("Product Does Not Exist yet.")
								isListed = False

						print("Row: " + str(row))
						print(self.orderList.item(row, 0).text())

						if isListed:
							print("Listed")
							"""updates anything if things have changed from quantity 
								to changes of product details from the database (untested)"""
							self.currentQuantity = int(self.orderList.item(row, 1).text())
							self.updatedQuantity = int(self.entryQuantity.text()) + self.currentQuantity
							self.updatedPrice = int(self.listPrice) * self.updatedQuantity

							self.orderList.item(row, 1).setText(str(self.updatedQuantity))
							self.orderList.item(row, 2).setText(str(self.listProdName))
							self.orderList.item(row, 3).setText(str(self.listPrice))
							self.orderList.item(row, 4).setText(str(self.updatedPrice))
						else:
							print("Not Yet Listed")
							if self.listProdID and self.listQty and self.listProdName and self.listPrice and self.listTotal is not None:
								self.orderList.insertRow(rowCount)

								self.orderList.setItem(rowCount, 0, QTableWidgetItem(str(self.listProdID)))
								self.orderList.setItem(rowCount, 1, QTableWidgetItem(str(self.listQty)))
								self.orderList.setItem(rowCount, 2, QTableWidgetItem(str(self.listProdName)))
								self.orderList.setItem(rowCount, 3, QTableWidgetItem(str(self.listPrice)))
								self.orderList.setItem(rowCount, 4, QTableWidgetItem(str(self.listTotal)))

						#self.lblTotalLabel.setText(str(self.totalPrice))
					self.totalPrice = 0

					for row in range(self.orderList.rowCount()):
							self.totalPrice += int(self.orderList.item(row, 4).text())

					self.lblTotalPriceLabel.setText(str(self.totalPrice) + " PHP")
				else:
					print("Product Not Found")



			

			"""
			# Get the row number of the selected item
			selected_row = self.orderList.currentRow()

			# Retrieve the data from the selected row
			column_count = self.orderList.columnCount()
			row_data = []
			for column in range(column_count):
				item = self.orderList.item(selected_row, column)
				row_data.append(item.text())

			self.query = "SELECT * FROM `tbl_productlist` WHERE `productID` = '" +  +"'"

			dbcursor.execute(self.query)
			con.commit()

			self.loadProductListNow()

			"""
		except ValueError:
			print("Enter numbers in Quantity only.")
			self.err = QMessageBox.critical(self, 'Invalid Input', 'Please enter numbers in Quantity.',
				QMessageBox.Ok)
		except Exception as e:
			print(e)

	def submitOrderNow(self):

		if self.orderList.rowCount() == 0:
			self.err = QMessageBox.critical(self, 'No Products Listed', 'Please add products first!',
					QMessageBox.Ok)
		else:
			print("Next Customer Button")
			self.generated_id = str(self.id_generator())

			for row in range(self.orderList.rowCount()):
				self.row_submitData = []
				for column in range(self.orderList.columnCount()):
					item = self.orderList.item(row, column)

					if item is not None:
						self.row_submitData.append(item.text())
					else:
						self.row_submitData.append('')
						#print(f"Item at ({row}, {column}): {item.text()}")

				print(self.generated_id, self.row_submitData[0], self.row_submitData[1], self.row_submitData[2], self.row_submitData[3], self.row_submitData[4])
				self.queryOrderContents = "INSERT INTO tbl_orderContents(order_id,  productID, orderQty, productName, price, orderPrice) VALUES (%s, %s, %s, %s, %s, %s)"
				self.queryOrderValues = (self.generated_id, self.row_submitData[0], self.row_submitData[1], self.row_submitData[2], self.row_submitData[3], self.row_submitData[4])
				dbcursor.execute(self.queryOrderContents, self.queryOrderValues)
				con.commit()

			formatted_date = datetime.date.strftime(datetime.date.today(), "%m/%d/%Y")
			self.queryOrderHistory = "INSERT INTO tbl_orderHistory(order_id, orderDate, totalPrice, cashierOnSession) VALUES (%s, %s, %s, %s)"
			self.queryHistoryValues = (self.generated_id, formatted_date, self.totalPrice, cashierHandler)
			dbcursor.execute(self.queryOrderHistory, self.queryHistoryValues)
			con.commit()

			self.err = QMessageBox.information(self, 'Order Confirmed', "Order Successfully Completed with a ID Number: " + self.generated_id + "!",
					QMessageBox.Ok)
			self.orderList.setRowCount(0)
			self.lblTotalPriceLabel.setText("0 PHP")
			self.entryProductID.clear()
			self.entryQuantity.clear()
		#check what data of eme
		#print(self.orderList.currentIndex().siblingAtColumn(0).data())
		""" helpful code sketch so hindi ko tatanggalin
		print(self.orderList.rowCount())

		print()

		for row in range(self.orderList.rowCount()):
			#print(item.text())
			if self.orderList.item(row, 0).text() == self.entryProductID.text().upper():
				print("Product Exists.")"""

	def orderHistoryNow(self):
		print("Order History Panel")
		try:
			self.openOtherWindow = True
			self.close()
			
			if self.isYes:	
				self.orderHistoryWindow = orderHistory()
				self.orderHistoryWindow.show()
			else:
				pass


		except Exception as e:
			print("An error occured: ")
			print(e)

	def productListingNow(self):
		print("Product Listing Panel")
		#initialize the window
		try:
			#initialize the app
			self.openOtherWindow = True
			self.close()

			print(self.isYes)
			if self.isYes:	
				self.productListingWindow = productListing()
				self.productListingWindow.show()
			else:
				pass

		except Exception as e:
			print("An error occured: ")
			print(e)

#  ____          _             _    _ _     _                      _____ ____  _____  ______  _____ 
# / __ \        | |           | |  | (_)   | |                    / ____/ __ \|  __ \|  ____|/ ____|
#| |  | |_ __ __| | ___ _ __  | |__| |_ ___| |_ ___  _ __ _   _  | |   | |  | | |  | | |__  | (___  
#| |  | | '__/ _` |/ _ \ '__| |  __  | / __| __/ _ \| '__| | | | | |   | |  | | |  | |  __|  \___ \ 
#| |__| | | | (_| |  __/ |    | |  | | \__ \ || (_) | |  | |_| | | |___| |__| | |__| | |____ ____) |
# \____/|_|  \__,_|\___|_|    |_|  |_|_|___/\__\___/|_|   \__, |  \_____\____/|_____/|______|_____/ 
#                                                          __/ |                                    
#                                                         |___/                                     


class orderHistory(QMainWindow):
	def closeEvent(self, event):
		if self.openOtherWindow:
			pass
		else:
			self.backToMainPOS = MainPOS()
			self.backToMainPOS.show()
	def __init__(self):
		self.openOtherWindow = False
		super(orderHistory, self).__init__()

		#load the ui file
		uic.loadUi('orderHistory.ui', self)

		#widget define
			#tables
		self.orderHistory = self.findChild(QTableWidget, "tblOrderHistory")
		self.orderHistory.setColumnWidth(0, 155)
		self.orderHistory.setColumnWidth(1, 160)
		self.orderHistory.setColumnWidth(2, 160)
		self.orderHistory.setColumnWidth(3, 160)
		self.orderHistory.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.orderHistory.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

			#buttons
		self.btnShowOrderHistory = self.findChild(QPushButton, "showHistory")
		self.btnShowOrderHistory.clicked.connect(self.loadOrderDetailsNow)

		self.btnRemoveOrderHistory = self.findChild(QPushButton, "removeHistory")
		self.btnRemoveOrderHistory.clicked.connect(self.deleteOrderDetailsNow)

		#disables window resize
		self.setFixedSize(self.size())

		self.loadOrderHistoryNow()

	def loadOrderHistoryNow(self):
		try:
			print("Loaded")
			print(cashierHandler)
			print("e")
			self.query = "SELECT * FROM tbl_orderHistory"
			tablerow = 0

			dbcursor.execute(self.query)
			self.res = dbcursor.fetchall()

			self.orderHistory.setRowCount(len(self.res))
			for self.row in self.res:
				self.orderHistory.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(self.row[0])))
				self.orderHistory.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(self.row[1]))
				self.orderHistory.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(self.row[2]))
				self.orderHistory.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(self.row[3]))
				tablerow += 1
				#print(self.row[0])

		except Exception as e:
			print(e)

	def loadOrderDetailsNow(self):
		self.selectedOrderIDIndex = self.orderHistory.currentIndex().siblingAtColumn(0).data()

		if self.selectedOrderIDIndex is None:
			self.err = QMessageBox.critical(self, 'No selected history', 'Please select an entry first.',
				QMessageBox.Ok)
		else:
			self.orderDetailsWindow = orderDetails(self.selectedOrderIDIndex)
			self.orderDetailsWindow.show()

	def deleteOrderDetailsNow(self):
		self.selectedOrderIDIndex = self.orderHistory.currentIndex().siblingAtColumn(0).data()

		if self.selectedOrderIDIndex is None:
			self.err = QMessageBox.critical(self, 'No selected history', 'Please select an entry to delete.',
				QMessageBox.Ok)
		else:
			queryDeleteOrderContents = "DELETE FROM tbl_orderContents WHERE order_id = '" + self.selectedOrderIDIndex + "'"
			queryDeleteOrderHistory = "DELETE FROM tbl_orderHistory WHERE order_id = '" + self.selectedOrderIDIndex + "'"
			dbcursor.execute(queryDeleteOrderContents)
			dbcursor.execute(queryDeleteOrderHistory)
			con.commit()
			self.loadOrderHistoryNow()


"""

	Order Details Window

"""

class orderDetails(QMainWindow):

	def __init__(self, orderID):
		super(orderDetails, self).__init__()

		self.orderID = orderID

		print(orderID)

		#load the ui file
		uic.loadUi('orderDetails.ui', self)

		#widget define
			#labels
		self.orderIDLabel = self.findChild(QLabel, "greetingLabel")
		self.orderIDLabel.setText("History for Order Number: " + self.orderID)
		self.orderCashierLabel = self.findChild(QLabel, "cashierLabel")
		self.orderDateLabel = self.findChild(QLabel, "dateLabel")
		self.orderTotalLabel = self.findChild(QLabel, "totalPriceLabel")

			#tables
		self.orderHistoryList = self.findChild(QTableWidget, "tblOrderList")
		self.orderHistoryList.setColumnWidth(0, 100)
		self.orderHistoryList.setColumnWidth(1, 50)
		self.orderHistoryList.setColumnWidth(2, 389)
		self.orderHistoryList.setColumnWidth(3, 50)
		self.orderHistoryList.setColumnWidth(4, 50)
		self.orderHistoryList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.orderHistoryList.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

			#buttons
		self.btnCloseWindow = self.findChild(QPushButton, "closeWindow")
		self.btnCloseWindow.clicked.connect(lambda: self.close())

		#disables window resize
		self.setFixedSize(self.size())

		self.loadOrderDetailsNow()

	def loadOrderDetailsNow(self):
		try:
			"""
				print("Loaded")
				print(cashierHandler)
				print("e")
			"""
			self.query = "SELECT productID, orderQty, productName, price, orderPrice FROM tbl_ordercontents WHERE order_id = '" + self.orderID + "'"
			tablerow = 0

			dbcursor.execute(self.query)
			self.res = dbcursor.fetchall()

			self.orderHistoryList.setRowCount(len(self.res))
			for self.row in self.res:
				self.orderHistoryList.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(self.row[0])))
				self.orderHistoryList.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(self.row[1]))
				self.orderHistoryList.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(self.row[2]))
				self.orderHistoryList.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(self.row[3]))
				self.orderHistoryList.setItem(tablerow, 4, QtWidgets.QTableWidgetItem(self.row[4]))
				tablerow += 1
				#print(self.row[0])

			self.res = []

			self.query = "SELECT orderDate, totalPrice, cashierOnSession FROM tbl_orderhistory WHERE order_id = '" + self.orderID + "'"
			dbcursor.execute(self.query)
			self.res = dbcursor.fetchone()

			#print(self.res[0], self.res[1], self.res[2])
			self.orderDateLabel.setText("Date: " + self.res[0])
			self.orderTotalLabel.setText(self.res[1] + " PHP")
			self.orderCashierLabel.setText("Cashier: " + self.res[2])

		except Exception as e:
			print(e)



#  _____               _            _     _      _     _   _                _____ ____  _____  ______  _____ 
# |  __ \             | |          | |   | |    (_)   | | (_)              / ____/ __ \|  __ \|  ____|/ ____|
# | |__) | __ ___   __| |_   _  ___| |_  | |     _ ___| |_ _ _ __   __ _  | |   | |  | | |  | | |__  | (___  
# |  ___/ '__/ _ \ / _` | | | |/ __| __| | |    | / __| __| | '_ \ / _` | | |   | |  | | |  | |  __|  \___ \ 
# | |   | | | (_) | (_| | |_| | (__| |_  | |____| \__ \ |_| | | | | (_| | | |___| |__| | |__| | |____ ____) |
# |_|   |_|  \___/ \__,_|\__,_|\___|\__| |______|_|___/\__|_|_| |_|\__, |  \_____\____/|_____/|______|_____/ 
#                                                                   __/ |                                    
#                                                                  |___/      


class productListing(QMainWindow):
	def closeEvent(self, event):
		if self.openOtherWindow:
			pass
		else:
			self.backToMainPOS = MainPOS()
			self.backToMainPOS.show()
	def __init__(self):
		self.openOtherWindow = False
		super(productListing, self).__init__()

		#load the ui file
		uic.loadUi('productListing.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

		#show the ui
		#self.show()

		#widget define

		#tables
		self.orderList = self.findChild(QTableWidget, "tblProductList")
		self.orderList.setColumnWidth(0, 5)
		self.orderList.setColumnWidth(1, 80)
		self.orderList.setColumnWidth(2, 430)
		self.orderList.setColumnWidth(3, 75)

			#buttons
		self.btnAddProduct = self.findChild(QPushButton, "addProduct")
		self.btnRemoveProduct = self.findChild(QPushButton, "removeProduct")
		self.btnEditProduct = self.findChild(QPushButton, "editProduct")
		self.btnRefreshTable = self.findChild(QPushButton, "manageCashier")

		#adding/connecting functions to buttons
		self.btnAddProduct.clicked.connect(self.addProductNow)
		self.btnEditProduct.clicked.connect(self.editProductNow)
		self.btnRemoveProduct.clicked.connect(self.removeProductNow)
		self.btnRefreshTable.clicked.connect(self.gotoManageCashier)

		self.loadProductListNow()
	
	def loadProductListNow(self):
		try:
			print("Loaded")
			print(cashierHandler)
			print("e")
			self.query = "SELECT * FROM tbl_productList"
			tablerow = 0

			dbcursor.execute(self.query)
			self.res = dbcursor.fetchall()

			self.orderList.setRowCount(len(self.res))
			for self.row in self.res:
				self.orderList.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(self.row[0])))
				self.orderList.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(self.row[1]))
				self.orderList.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(self.row[2]))
				self.orderList.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(self.row[3]))
				tablerow += 1
				#print(self.row[0])

		except Exception as e:
			print(e)

	def addProductNow(self):
		self.openOtherWindow = True
		self.close()
		self.addProductWindow = addProduct()
		self.addProductWindow.show()

	def removeProductNow(self):
		try:
			# Get the row number of the selected item
			selected_row = self.orderList.currentRow()

			# Retrieve the data from the selected row
			column_count = self.orderList.columnCount()
			row_data = []
			for column in range(column_count):
				item = self.orderList.item(selected_row, column)
				row_data.append(item.text())

			self.query = "DELETE FROM tbl_productList WHERE id = '"+ row_data[0] + "'"

			dbcursor.execute(self.query)
			con.commit()

			self.loadProductListNow()

		except AttributeError:
			self.err = QMessageBox.critical(self, 'No selected product', 'Please select an item to delete.',
				QMessageBox.Ok)
		except Exception as e:
			print(e)

	def editProductNow(self):
		self.selectedProductIDIndex = self.orderList.currentIndex().siblingAtColumn(1).data()
		
		if self.selectedProductIDIndex is None:
			self.err = QMessageBox.critical(self, 'No selected product', 'Please select an item to edit.',
				QMessageBox.Ok)
		else:
			self.openOtherWindow = True
			self.close()
			self.editProductWindow = editProduct(self.selectedProductIDIndex)
			self.editProductWindow.show()

	def gotoManageCashier(self):
		self.openOtherWindow = True
		self.close()
		self.manageCashierWindow = cashierManager()
		self.manageCashierWindow.show()

"""
	Add Product Window - Under Product Listing Window

"""

class addProduct(QMainWindow):
	def closeEvent(self, event):
		self.backToProductListing = productListing()
		self.backToProductListing.show()

	def __init__(self):
		super(addProduct, self).__init__()

		#load the ui file
		uic.loadUi('addProduct.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

		#show the ui
		#self.show()

		#widget define

			#buttons
		self.btnConfirmAddProduct = self.findChild(QPushButton, "confirmAddProduct")

			#entry
		self.entryProductName = self.findChild(QLineEdit, "entryProductName")
		self.entryProductSN = self.findChild(QLineEdit, "entryProductSN")
		self.entryProductPrice = self.findChild(QLineEdit, "entryProductPrice")

		#adding/connecting functions to buttons
		self.btnConfirmAddProduct.clicked.connect(self.confirmAddProductNow)

	def confirmAddProductNow(self):
		try:
			self.checkQuery = "SELECT * FROM `tbl_productlist` WHERE `productID` = '" + self.entryProductSN.text() +"'"
			dbcursor.execute(self.checkQuery)

			self.checkRes = dbcursor.fetchone()

			print(self.checkRes)

			if self.checkRes:
				self.err = QMessageBox.critical(self, 'Product Exists', 'Please enter a different Product ID or S/N.',
				QMessageBox.Ok)
			else:
				self.productPriceEnter = int(self.entryProductPrice.text())
				self.query = "INSERT INTO tbl_productList(productID, productName, price) VALUES (%s, %s, %s)"
				self.values = (self.entryProductSN.text().upper(), self.entryProductName.text().upper(), self.productPriceEnter)
				dbcursor.execute(self.query, self.values)
				con.commit()
				print("Done")
				self.err = QMessageBox.information(self, 'Product Added', 'Successfully added product.',
				QMessageBox.Ok)
				self.backToProductListing = productListing()
				self.backToProductListing.show()
				self.close()
		except ValueError:
			self.err = QMessageBox.critical(self, 'Invalid Input', 'Please enter numbers in Price.',
				QMessageBox.Ok)
			"""except Exception as e:
				print("An error occured.")
				print(e)"""



"""
	Edit Product Window - Under Product Listing Window

"""


class editProduct(QMainWindow):
	def closeEvent(self, event):
		self.backToProductListing = productListing()
		self.backToProductListing.show()

	def __init__(self, productID):
		super(editProduct, self).__init__()

		#load the ui file
		uic.loadUi('editProduct.ui', self)

		#placeholder ng product id/sn kasi ayaw mabasa sa editproductnow function
		self.productID = productID

		#widget define
			#label texts
		self.lblProductIDPlaceholder = self.findChild(QLabel, "productIDPlaceholder")

			#buttons
		self.btnConfirmEditProduct = self.findChild(QPushButton, "confirmEditProduct")

			#entry
		self.entryProductName = self.findChild(QLineEdit, "productName")
		self.entryProductPrice = self.findChild(QLineEdit, "productPrice")

		self.lblProductIDPlaceholder.setText("Edit Product for S/N: " + str(self.productID))

		#adding/connecting function to buttons
		self.btnConfirmEditProduct.clicked.connect(self.editProductNow)

		#disables window resize
		self.setFixedSize(self.size())

		#show the ui
		#self.show()

	def editProductNow(self):
		print(self.productID)
		print(self.entryProductName.text())
		print(self.entryProductPrice.text())

		self.productPriceEnter = int(self.entryProductPrice.text())
		self.query = "UPDATE tbl_productlist SET productName = %s, price = %s WHERE productID = %s"
		self.values = (self.entryProductName.text().upper(), self.entryProductPrice.text(), self.productID)
		dbcursor.execute(self.query, self.values)
		con.commit()

		print("Done")

		self.close()

#   _____          _     _              _____ ____  _____  ______  _____ 
#  / ____|        | |   (_)            / ____/ __ \|  __ \|  ____|/ ____|
# | |     __ _ ___| |__  _  ___ _ __  | |   | |  | | |  | | |__  | (___  
# | |    / _` / __| '_ \| |/ _ \ '__| | |   | |  | | |  | |  __|  \___ \ 
# | |___| (_| \__ \ | | | |  __/ |    | |___| |__| | |__| | |____ ____) |
#  \_____\__,_|___/_| |_|_|\___|_|     \_____\____/|_____/|______|_____/ 
#

class cashierManager(QMainWindow):
	def closeEvent(self, event):
		if self.openOtherWindow:
			pass
		else:
			self.backToProductListing = productListing()
			self.backToProductListing.show()

	def __init__(self):
		super(cashierManager, self).__init__()

		self.openOtherWindow = False

		#load the ui file
		uic.loadUi('cashierManage.ui', self)

		#disables window resize
		self.setFixedSize(self.size())

		#widget define
			#buttons
		self.btnAddCashier = self.findChild(QPushButton, "addCashier")
		self.btnAddCashier.clicked.connect(self.addCashierWindow)

		self.btnRemoveCashier = self.findChild(QPushButton, "removeCashier")
		self.btnRemoveCashier.clicked.connect(self.removeCashierNow)

		self.btnChangePass = self.findChild(QPushButton, "changePass")
		self.btnChangePass.clicked.connect(self.changePassWindow)

			#table
		self.cashierList = self.findChild(QTableWidget, "tblCashier")

		self.loadCashierListNow()

	def loadCashierListNow(self):
		try:
			print("Loaded")
			print(cashierHandler)
			print("e")
			self.query = "SELECT id, cashierName, registrationDate FROM tbl_cashierlist"
			tablerow = 0

			dbcursor.execute(self.query)
			self.res = dbcursor.fetchall()

			self.cashierList.setRowCount(len(self.res))
			for self.row in self.res:
				self.cashierList.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(self.row[0])))
				self.cashierList.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(self.row[1]))
				self.cashierList.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(self.row[2]))
				tablerow += 1
				#print(self.row[0])

		except Exception as e:
			print(e)

	def addCashierWindow(self):
		self.openOtherWindow = True
		self.close()
		self.goToAddCashierWindow = addCashier()
		self.goToAddCashierWindow.show()

	def removeCashierNow(self):
		self.selectedOrderIDIndex = self.cashierList.currentIndex().siblingAtColumn(0).data()
		if self.selectedOrderIDIndex is None:
			self.err = QMessageBox.critical(self, 'No Account Selected', 'Please select a user to remove.',
				QMessageBox.Ok)
		elif self.selectedOrderIDIndex == '1':
			self.err = QMessageBox.critical(self, 'Cannot Delete user0!', 'Please select another user to remove.',
				QMessageBox.Ok)
		else:
			self.query = "DELETE FROM tbl_cashierlist WHERE id = '" + self.selectedOrderIDIndex + "'"
			dbcursor.execute(self.query)
			con.commit()
			self.loadCashierListNow()

	def changePassWindow(self):
		self.selectedOrderIDIndex = self.cashierList.currentIndex().siblingAtColumn(0).data()
		self.selectedOrderIDIndexByName = self.cashierList.currentIndex().siblingAtColumn(1).data()

		if self.selectedOrderIDIndex is None:
			self.err = QMessageBox.critical(self, 'No Account Selected', 'Please select a user first.',
				QMessageBox.Ok)
		else:
			self.openOtherWindow = True
			self.close()
			self.goToChangePassword = changePass(self.selectedOrderIDIndex, self.selectedOrderIDIndexByName)
			self.goToChangePassword.show()

class addCashier(QMainWindow):
	def closeEvent(self, event):
		self.backToCashierManager = cashierManager()
		self.backToCashierManager.show()

	def __init__(self):
		super(addCashier, self).__init__()

		#load the ui file
		uic.loadUi('addCashier.ui', self)

		#widget define
			#entries
		self.entryUsername = self.findChild(QLineEdit, "cashierNameEntry")
		self.entryPassword = self.findChild(QLineEdit, "cashierPasswordEntry")
			#buttons
		self.btnAddCashier = self.findChild(QPushButton, "confirmAddCashier")
		self.btnAddCashier.clicked.connect(self.addCashierNow)

		#disables window resize
		self.setFixedSize(self.size())

	def addCashierNow(self):
		print(self.entryUsername.text())
		print(self.entryPassword.text())
		if len(self.entryPassword.text()) < 8:
			self.err = QMessageBox.critical(self, 'Insecure Credentials', 'Enter at least 8 characters minimum.',
				QMessageBox.Ok)
		else:
			self.formatted_date = datetime.date.strftime(datetime.date.today(), "%m/%d/%Y")
			self.query = "INSERT INTO tbl_cashierList(cashierName, registrationDate, cashierPassword) VALUES ('" + self.entryUsername.text() + "', '" + self.formatted_date + "', md5('" + self.entryPassword.text() + "'))"
			dbcursor.execute(self.query)
			con.commit()
			self.err = QMessageBox.information(self, 'Creation Successful', "Cashier " + self.entryUsername.text() +" created!",
				QMessageBox.Ok)
			self.close()

class changePass(QMainWindow):
	def closeEvent(self, event):
		self.backToCashierManager = cashierManager()
		self.backToCashierManager.show()

	def __init__(self, cashierId, cashierName):
		super(changePass, self).__init__()

		self.cashierId = cashierId
		self.cashierName = cashierName

		print(self.cashierId, self.cashierName)


		#load the ui file
		uic.loadUi('cashierChangePassword.ui', self)

		#widget define
			#label
		self.cashierNamePlaceholder = self.findChild(QLabel, "cashierNamePlaceholder")
			#button

		self.changePassButton = self.findChild(QPushButton, "confirmChangePass")
		self.changePassButton.clicked.connect(self.changePassNow)
			#entry
		self.entryNewPassword = self.findChild(QLineEdit, "newPass")


		#disables window resize
		self.setFixedSize(self.size())

	def changePassNow(self):
		print(self.entryNewPassword.text())
		if len(self.entryNewPassword.text()) < 8:
			self.err = QMessageBox.critical(self, 'Insecure Credentials', 'Enter at least 8 characters minimum.',
				QMessageBox.Ok)
		else:
			self.query = "UPDATE tbl_cashierlist SET cashierPassword = md5('" + self.entryNewPassword.text() + "') WHERE id = '" + self.cashierId + "'"
			dbcursor.execute(self.query)
			con.commit()
			self.err = QMessageBox.information(self, "Password Changed Successfully", "Password for Cashier " + self.cashierName + " has been changed.",
				QMessageBox.Ok)
			self.close()
			self.backToCashierManager = cashierManager()
			self.backToCashierManager.show()

#  _____             _   _                   _____ ____  _____  ______ 
# |  __ \           | | (_)                 / ____/ __ \|  __ \|  ____|
# | |__) |   _ _ __ | |_ _ _ __ ___   ___  | |   | |  | | |  | | |__   
# |  _  / | | | '_ \| __| | '_ ` _ \ / _ \ | |   | |  | | |  | |  __|  
# | | \ \ |_| | | | | |_| | | | | | |  __/ | |___| |__| | |__| | |____ 
# |_|  \_\__,_|_| |_|\__|_|_| |_| |_|\___|  \_____\____/|_____/|______|
                                                                      

#initial startup of the program

if __name__ == "__main__":
	def closeProgram():
		print("Bye")
		sys.exit()

	try:
		#initialize the app
		app = QApplication(sys.argv)
		MainUIWindow = loginScreen()
		MainUIWindow.show()
		app.exec_()
		app.aboutToQuit.connect(closeProgram)

	except Exception as e:
		print("An error occured: ")
		print(e)

