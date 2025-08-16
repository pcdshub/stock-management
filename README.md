<img src="assets/images/slac_logo.jpg" alt="SLAC-LCLS" width="200" style="float:right; border-radius: 20px;">

# SLAC-LCLS Stock Management

An application for managing inventory and stock for the SLAC National Accelerator Laboratory's LCLS division. This
tool streamlines inventory tracking, integrates QR code scanning, and connects to Google Sheets for lightweight,
cloud-based data storage.

---

## Features

- **Dual Interface**
  <br>
  Seamless GUI for ease-of-use and a powerful CLI for fast, scriptable control.

- **Inventory Table View:**
  <br>
  Browse, search, update, and remove inventory from a table view, resembling a Google Sheet.

- **Restock Status Flags**
  <br>
  Clearly indicates whether items are fully stocked, low, or pending replenishment.

- **QR Code Scanning & Generation:**
  <br>
  Scan both item and user QR codes with your webcam or camera to quickly log users in, look up, and manage inventory
  items. Additionally, generate QR codes for new stock entries.

- **Data Export & File Generation**
  <br>
  Export inventory data to multiple formats such as CSV or PDF for analysis and reporting.

- **Redundant Dual Data Storage System**
  <br>
  Utilizes both SQL and Google Sheets to ensure consistent, recoverable record-keeping.

- **Live Inventory Tracking**
  <br>
  Real-time synchronization between physical stock, GUI, CLI, and both databases.

- **Modular Architecture:**
  <br>
  Components are cleanly separated into controllers, utilities, and UI for easy extension.

- **Robust Logging:**
  <br>
  All application events and errors are logged thoroughly for troubleshooting and auditing.

- **Asynchronous Programming:**
  <br>
  The application uses asynchronous programming techniques to keep the user interface responsive during
  time-consuming operations like video capture, QR code scanning, and database access without freezing or lagging.
  This ensures a smooth and efficient user experience, even when multiple actions happen simultaneously.

- **Portable & Scalable**
  <br>
  Designed to scale with the division's needs and is adaptable for future hardware integrations.

---

## Getting Started

### Prerequisites

- Python 3.9 or newer
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)
- Google Cloud service account with access
  to [Google Sheets API](https://developers.google.com/sheets/api/quickstart/python)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pcdshub/stock-management.git
   cd stock-management
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Main dependencies include:
	- PyQt5
	- opencv-python
	- numpy
	- gspread
	- oauth2client
	- pathlib
	- typing
	- qasync
	- qrcode
	- qtawesome
	- mysql
	- prettytable
	- pytest
	- pytest-qt

3. **Configure your Google Sheet:**
	- Create or open a Google Sheets document that will act as your stock database.
	- Name the file and change `contants.py` -> `GS_FILE_NAME` to match the file name.
	- Make sure your sheet includes two separate tabs (worksheets):
	    - One named "Master Part List" — this should store all inventory items, quantities, and related details.
          - This sheet should have specific columns which are listed in `constants.py` as `KEEP_HEADERS`.
		- One named "Users" — this should store usernames for access control, logging, or tracking who checks out stock.
          - All usernames should be placed in the first column.
	- Follow [these instructions](https://gspread.readthedocs.io/en/latest/oauth2.html) to create a Google Cloud service
	  account and rename the `.json` file as `gs_credentials.json`.
	- Share your Google Sheet with the service account.
	- Place `gs_credentials.json` in the `assets/` directory.

4. **(Optional) Configure your MySQL database:**
	- **Install MySQL:** Download and install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/).
    - **Start the MySQL Server:** On most systems this happens automatically after installation, but you can start
      it manually with:
      ```bash
      net start MySQL
      ```
    - **Log into MySQL as root:**
      ```bash
      mysql -u root -p
      ```
    - **Create, use, and source the database with MySQL:**
      ```sql
      CREATE DATABASE common_stock
      USE common_stock
      SOURCE /path/to/dump/file.sql
      ```

5. **Running the application:**
	- **Run The GUI**
	  To launch the application in GUI mode, just use the --run or -r flag:
	   ```bash
	   python -m stock_manager --run
	   ```
	  This opens the full graphical interface for managing inventory, scanning items, and generating reports.
	- **Use Command-Line Options**
	  You can also use CLI commands to perform specific tasks directly from the terminal. For example:
	  ```bash
	  python -m stock_manager users --list
	  python -m stock_manager items remove part_num
	  python -m stock_manager sync
	  python -m stock_manager qr part_num ./exports
	  python -m stock_manager --version
	  python -m stock_manager -r
	  ```
	  Use `--help` to see all available CLI options for any command:
	  ```bash
      python -m stock_manager --help
      python -m stock_manager items --help
      python -m stock_manager users --help
      python -m stock_manager qr --help
      python -m stock_manager export --help
	  ```
      Use `--tree` to see all commands in a tree layout:
      ```bash
      python -m stock_manager --tree
      ```
      ```
      ├── help - ...
      ├── test - ...
      ├── sync - ...
      ├── export - ...
      │   ├── help - ...
      │   ├── extension - ...
      │   └── path - ...
      └── ...
      ```

---

## Usage

- **View & Manage Inventory**
  The main screen displays a live-synced table with your Google Sheet database. Changes made in the app or CLI are
  reflected automatically—no need to worry about syncing one database over another.

- **QR Code Scanning for Items & Login**
  On the QR Scanner and Login pages, users can scan item QR codes to look up inventory or scan their personal QR
  code to log in. Scanned events are timestamped and logged.

- **Generate QR Codes**
  Use the "Generate QR" page to create QR codes for items or users. Choose the target item, destination folder, and
  click **Download** to export a QR image file.

- **Command Line Interface (CLI)**
  Run `python -m stock_manager` to launch the GUI or pass additional CLI flags for command-line tasks (e.g.,
  exporting data, printing inventory, or syncing databases). Run `--help` for a full list of options.

- **Export Data**
  Export inventory data to various file formats (e.g., `.csv`, `.pdf`, etc.) through the GUI or CLI.

- **Database Synchronization**
  The local MySQL database is automatically synchronized to the state of the Google Sheet. You’ll
  never have to worry about one database being out of date.

- **Logging**
  All significant events (logins, scans, syncs, errors) are logged to `app.log` for auditing and debugging.

- **Navigation**
  Use the sidebar to switch between pages (Inventory, Scanner, QR Generator, etc.) or to log out and exit the
  application.

---

## Project Structure

```
stock-management/
│
├── stock_manager/          # Main application code
│   ├── app.py
│   ├── app.log
│   ├── __main__.py
│   ├── cli.py
│   │
│   ├── controllers/
│   │   ├── abstract.py
│   │   ├── add.py
│   │   ├── edit.py
│   │   ├── export.py
│   │   ├── finish.py
│   │   ├── remove.py
│   │   ├── scanner.py
│   │   └── view.py
│   │
│   ├── model/
│   │   └── item.py
│   │
│   ├── utils/
│   │   ├── constants.py
│   │   ├── database.py
│   │   ├── enums.py
│   │   ├── file_exports.py
│   │   └── logger.py
│   │
│   └── ...
│
├── ui/                     # Qt Designer .ui files
│   ├── *.ui
│   └── ...
│
├── assets/
│   ├── gs_credentials.json # Google Sheets credentials
│   ├── resources.qrc
│   │
│   ├── images/             # Images used throughout application
│   │   └── ...
│   │
│   └── ...
│
├── exports/                # Default Exports Location
│   └── ...
│
├── dumps/                  # Default SQL Backup Dumps Location
│   ├── inventory/          # Inventory Database Dumps
│   │   └── ...
│   │
│   ├── users/              # User Database Dumps
│   │   └── ...
│   └── ...
│
├── launcher.sh
├── setup.py
├── requirements.txt
└── README.md
```

---

## Error Handling

- All critical operations (UI loading, database access, camera access) are wrapped in error handlers.
- Users are presented with clear messages in case of failure (e.g., camera not found, Google Sheets inaccessible).
- Detailed errors are logged for troubleshooting.
- Error messages are also printed to the console for CLI use.

---

## Customization

- **To use a different Google Sheet:**
  Change the file or sheets names in `database.py`.

- **To modify the UI:**
  Edit the `.ui` files in the `ui/` directory using [Qt Designer](https://build-system.fman.io/qt-designer-download).

- **To add new features/screens:**
  Extend the `controllers/` or `utils/` package as needed.

- **To add new commands:**
  Add commands in `cli.py` accordingly.

- **To run tests:**
  Add test modules to `tests/` as needed.

- **To Develop New Features:**
  Add WIP modules to `scripts/` before implementing into project.

---

## License

This project is licensed under the SLAC National Accelerator Laboratory License.

---

## Acknowledgements

- [SLAC National Accelerator Laboratory](https://www6.slac.stanford.edu/)
- [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html)
- [OpenCV](https://opencv.org/)
- [gspread](https://gspread.readthedocs.io/)
- [PyTest](https://docs.pytest.org/en/stable/)
