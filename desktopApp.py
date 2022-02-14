import os, sys
import http.server

# from PyQt5 import QtCore
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QMessageBox
# from PyQt5.QtWidgets import QGridLayout, QPushButton, QComboBox, QFileDialog
from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QMessageBox
from qtpy.QtWidgets import QGridLayout, QPushButton, QComboBox, QFileDialog
from qtpy.QtGui import QFont

# from qtpy.uic import loadUi

import readalongs.api
# from readalongs.align import create_input_tei
# from readalongs.text.util import save_xml
from readalongs.util import get_langs

HOST = "127.0.0.1"
PORT = 7000
DIRECTORY = "output"
TEXT_FONT = "Optima"
BUTTON_SIZE = 18
TITLE_SIZE = 48

style = """
QWidget {
    background-color: white;
    font: Optima;
} 

QLabel {
    
    font-size: 20px;
    color: #006325;     
}        

QPushButton {
    background-color: #006325;
    font: Optima;
    font-size:18px;
    color: white;

    min-width:  80;
    max-width:  140px;
    min-height: 80px;
    max-height: 140px;

    border-radius: 35px;        
    border-width: 1px;
    border-color: #9A660B;
    border-style: solid;
}
QPushButton:hover {
    background-color: #328930;
}
QPushButton:pressed {
    background-color: #80c342;
}    

"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


class HttpDaemon(QtCore.QThread):
    def run(self):
        self._server = http.server.HTTPServer((HOST, PORT), Handler)
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()
        self._server.socket.close()
        # self.wait()


class readalongsUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Readlongs App")
        self.setMinimumSize(1180, 766)

        self.generalLayout = QGridLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self._createDisplay()
        self._createButtons()
        # TODO: here we only mimic the config from Studio
        #       need to add options later.
        self.config = {
            "language": "",
            "textfile": "",
            "audiofile": "",
            "xmlfile": "",
            "tokfile": "",
            "force_overwrite": True,
            "output_base": os.path.join(os.getcwd(), "output"),
            "bare": False,
            "config": None,
            "unit": "w",
            "save_temps": False,
            "g2p_fallbacks": ["und"],
            "g2p_verbose": False,
        }

        self.httpd = HttpDaemon(self)

    def _createDisplay(self):
        helloMsg = QLabel("""<h1>Welcome to Readalongs!</h1>
            <p>Please upload the text file, audio file, 
            and mapping file you want readalongs to align.</p>""")
        helloMsg.setFont(QFont(TEXT_FONT, TITLE_SIZE))
        self.generalLayout.addWidget(helloMsg, 0, 1, 1, 2)

        extra_Msg = QLabel("""
            <p>ReadAlong Studio is an end-to-end audio/text <br>
            aligner where you can visualize the alignment of <br>
            your audio and text files for a specific language.</p>
            """)
        extra_Msg.setFont(QFont(TEXT_FONT, BUTTON_SIZE))
        self.generalLayout.addWidget(extra_Msg, 1, 1, 1, 3)

        # helloMsg.move(60, 15)
        upload_text_file_label = QLabel("Upload Text file")
        upload_text_file_label.setFont(QFont(TEXT_FONT, BUTTON_SIZE))
        self.generalLayout.addWidget(upload_text_file_label, 2, 1)

        self.textPathDisplay = QLabel("<i>Text file path:</i> None selected.")
        self.generalLayout.addWidget(self.textPathDisplay, 3, 1, 1, 3)

        upload_audio_file_label = QLabel("Upload Audio file")
        upload_audio_file_label.setFont(QFont(TEXT_FONT, BUTTON_SIZE))
        self.generalLayout.addWidget(upload_audio_file_label, 4, 1)

        self.audioPathDisplay = QLabel(
            "<i>Audio file path:</i> None selected.")
        self.generalLayout.addWidget(self.audioPathDisplay, 5, 1, 1, 3)

        upload_mapping_label = QLabel("Upload Mapping")
        upload_mapping_label.setFont(QFont(TEXT_FONT, BUTTON_SIZE))
        self.generalLayout.addWidget(upload_mapping_label, 6, 1)

    def _createButtons(self):
        uploadTextButton = QPushButton("Browse")
        self.generalLayout.addWidget(uploadTextButton, 2, 4, 1, 1)
        uploadTextButton.clicked.connect(self.getTextFile)

        uploadAudioButton = QPushButton("Browse")
        self.generalLayout.addWidget(uploadAudioButton, 4, 4, 1, 1)
        uploadAudioButton.clicked.connect(self.getAudioFile)

        # grab the language dynamically

        langs, lang_names = get_langs()
        self.mappingOptions = [f"{l} ({lang_names[l]})" for l in langs]
        self.mappingDropDown = QComboBox()
        self.mappingDropDown.addItems(self.mappingOptions)
        self.generalLayout.addWidget(self.mappingDropDown, 7, 1, 1, 2)
        self.mappingDropDown.currentTextChanged.connect(self.selectMapping)

        # mappingConfirmButton = QPushButton("Confirm")
        # self.generalLayout.addWidget(mappingConfirmButton, 6, 4, 1, 1)
        # mappingConfirmButton.clicked.connect(self.selectMapping)

        # self.NextButton = QPushButton("Next Step")
        self.NextButton = QPushButton("Align your files")
        self.NextButton.setFont(QFont(TEXT_FONT, BUTTON_SIZE))
        self.NextButton.setSizePolicy(100, 120)
        self.generalLayout.addWidget(self.NextButton, 8, 1)
        self.NextButton.clicked.connect(self.callMajorProcess)

    def selectMapping(self):
        self.config["language"] = self.mappingDropDown.currentText().split(
            " ")[0]
        # self.popupMessage("LANGS = " + self.config["language"]) # debug use.

    def getTextFile(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a text file",
            directory=os.getcwd(),
            filter=
            "Text File (*.txt *csv *.xml);;Just another type (*.mp3 *.mp4)",
            initialFilter="Text File (*.txt *csv *.xml)",
        )
        self.config["textfile"] = response[0]
        # grab the filename here:
        self.config["filename"] = os.path.basename(response[0]).split(".")[0]
        self.textPathDisplay.setText("<i>Text file path:</i> " + response[0])
        return response

    def getAudioFile(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a audio file",
            directory=os.getcwd(),
            filter="Audio File (*.mp3 *.mp4)",
            initialFilter="Audio File (*.mp3 *.mp4)",
        )
        self.config["audiofile"] = response[0]
        self.audioPathDisplay.setText("<i>Audio file path:</i> " + response[0])
        return response

    def popupMessage(self, message):
        popup = QMessageBox()
        popup.setWindowTitle("Message:")
        popup.setText(message)
        popup.setGeometry(100, 200, 100, 100)
        popup.exec_()

    def callMajorProcess(self):
        """
        2. readalongs prepare - remove
        3. tokenize - remove
        4. g2p - remove
        1. readalongs align
        5. call an interactive web
        """
        # input check
        try:
            if not all([
                    self.config["language"],
                    self.config["textfile"],
                    self.config["audiofile"],
            ]):
                self.popupMessage(
                    "At least one of the following three parameters is \
                        missing: text file path, audio file path, mapping.")
                return  # kill and go back

            self.align()
            # self.prepare() # will require in version 2.
            # self.tokenize()
            # self.g2p()

            if self.NextButton.text() == "Align your files":
                self.httpd.start()
                self.NextButton.setText("Stop")
                self.NextButton.clicked.connect(self.stopServer)
                self.popupMessage(
                    f"Success! Go to localhost:{PORT} to see the result.")
        except Exception as e:
            self.popupMessage(f"Error: {e}")

    def stopServer(self):
        self.httpd.stop()
        self.NextButton.setText("Align your files")
        self.NextButton.clicked.connect(self.callMajorProcess)
        self.popupMessage(
            f"Successfully stopped server. Now you can resubmit new files.")

    def align(self):
        readalongs.api.align(
            textfile=self.config["textfile"],
            audiofile=self.config["audiofile"],
            output_base=self.config["output_base"],
            language=[self.config["language"], *self.config["g2p_fallbacks"]],
            force_overwrite=self.config["force_overwrite"],
            save_temps=self.config["save_temps"],
        )

    # def prepare(self):
    #     input_file = self.config["textfile"]
    #     if not self.config.get("xmlfile"):
    #         self.config["xmlfile"] = os.path.join(
    #             self.config["output_base"], save_filename + "-prep.xml"
    #         )

    #     out_file = self.config["xmlfile"]
    #     filehandle, filename = create_input_tei(
    #         input_file_name=input_file,
    #         text_language=self.config["language"],
    #         output_file=out_file,
    #     )


def main():
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    view = readalongsUI()
    view.show()

    # Create instances of the model and the controller
    # PyCalcController(view=view)

    # Execute calculator's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
