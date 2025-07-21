<img src="assets/images/slac_logo.jpg" alt="SLAC-LCLS" width="200" style="float:right; border-radius: 20px;">

# SLAC-LCLS Stock Management

An application for managing inventory and stock for the SLAC National Accelerator Laboratory's LCLS division. This 
tool streamlines inventory tracking, integrates QR code scanning, and connects to Google Sheets for lightweight, cloud-based data storage.

---

## Features

- **Inventory Table View:**  
  Browse, search, update, and remove inventory from a table view, resembling a Google Sheet.

- **QR Code Scanning:**  
  Scan both item and user QR codes with your webcam or camera to quickly log users in, look up, and manage inventory
  items.

- **Modular Architecture:**  
  Components are cleanly separated into controllers, utilities, and UI for easy extension.

- **Robust Logging:**  
  All application events and errors are logged thoroughly for troubleshooting and auditing.

- **Asynchronous Programming:**  
  The application uses asynchronous programming techniques to keep the user interface responsive during
  time-consuming operations like video capture, QR code scanning, and database access without freezing or lagging.
  This ensures a smooth and efficient user experience, even when multiple actions happen simultaneously.

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)
- Google Cloud service account with access to [Google Sheets API](https://developers.google.com/sheets/api/quickstart/python)

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

3. **Configure Your Google Sheet:**
    - Create or open a Google Sheets document that will act as your stock database.
    - Make sure your sheet includes two separate tabs (worksheets):
        - One named "Parts" — this should store all inventory items, quantities, and related details.
        - One named "Users" — this should store usernames for access control, logging, or tracking who checks out stock.
   - Follow [these instructions](https://gspread.readthedocs.io/en/latest/oauth2.html) to create a Google Cloud service account and download the `gs_credentials.json` key.
   - Share your Google Sheet (e.g., "Stock Management Sheet") with the service account email in your credentials file.
   - Place `gs_credentials.json` in the `assets/` directory.

4. **Run the application:**
   ```bash
   python -m stock_manager
   ```

---

## Usage

- **View Inventory:**  
  The main screen shows a table synced with your Google Sheet. Data is read directly from the sheet.

- **Scan QR Codes:**  
  Switch to the QR Scanner page. Hold item QR codes up to your camera to scan them. Scanned codes are logged and can be
  used for lookup or management.

- **Navigation:**  
  Use the sidebar to switch between screens or exit the application.

- **Logging:**  
  Most actions and errors are logged to `app.log` for troubleshooting and auditing.

---

## Project Structure

```
stock-management/
│
├── stock_manager/          # Main application code
│   ├── app.py
│   ├── app.log
│   ├── __main__.py
│   │
│   ├── controllers/
│   │   ├── abstract.py
│   │   ├── view.py
│   │   ├── scanner.py
│   │   ├── add.py
│   │   ├── edit.py
│   │   ├── remove.py
│   │   ├── export.py
│   │   └── finish.py
│   │
│   ├── model/
│   │   └── item.py
│   │
│   ├── utils/
│   │   ├── constants.py
│   │   ├── logger.py
│   │   ├── enums.py
│   │   ├── file_exports.py
│   │   ├── qr_generator.py
│   │   └── database.py
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
│   ├── icons/              # Icons used throughout application
│   │   └── ...
│   │
│   ├── images/             # Images used throughout application
│   │   └── ...
│   │
│   └── ...
│
├── exports/                # Default Exports Location
│   └── ...
│
├── setup.py
├── requirements.txt
└── README.md
```

---

## Error Handling

- All critical operations (UI loading, database access, camera access) are wrapped in error handlers.
- Users are presented with clear messages in case of failure (e.g., camera not found, Google Sheets inaccessible).
- Detailed errors are logged for troubleshooting.

---

## Customization

- **To use a different Google Sheet:**  
  Change the file or sheets names in `database.py`.

- **To modify the UI:**  
  Edit the `.ui` files in the `ui/` directory using [Qt Designer](https://build-system.fman.io/qt-designer-download).

- **To add new features/screens:**  
  Extend the `controllers/` or `utils/` package as needed.

---

## License

This project is licensed under the SLAC National Accelerator Laboratory License.

---

## Acknowledgements

- [SLAC National Accelerator Laboratory](https://www6.slac.stanford.edu/)
- [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html)
- [OpenCV](https://opencv.org/)
- [gspread](https://gspread.readthedocs.io/)