import os, sys
import http.server
import socketserver

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

from readalongs.align import create_input_tei, align_audio
from readalongs.text.util import save_txt, save_xml, save_minimal_index_html
from readalongs.util import getLangs, parse_g2p_fallback
from readalongs.log import LOGGER

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
            "text_input": True,
            "force_overwrite": True,
            "output_base": os.path.join(os.getcwd(), "output"),
            "bare": False,
            "config": None,
            "closed_captioning": False,
            "debug": True,
            "unit": "w",
            "save_temps": False,
            "text_grid": False,
            "output_xhtml": False,
            "g2p_fallback": None,
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

        langs, lang_names = getLangs()
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
        temp_base = None
        # if text, turn to xml first
        if self.config["textfile"].split(".")[-1] == "txt":
            tempfile, xml_textfile = create_input_tei(
                input_file_name=self.config["textfile"],
                text_language=self.config["language"],
                save_temps=temp_base,
            )
        elif self.config["textfile"].split(".")[-1] == "xml":
            xml_textfile = self.config["textfile"]
        else:
            raise TypeError("Only accept a txt file or xml file.")

        results = align_audio(
            xml_textfile,
            self.config["audiofile"],
            unit=self.config["unit"],
            bare=self.config["bare"],
            config=self.config["config"],
            save_temps=temp_base,
            g2p_fallbacks=parse_g2p_fallback(self.config["g2p_fallback"]),
            verbose_g2p_warnings=self.config["g2p_verbose"],
        )

        # save the files into local address
        from readalongs.text.make_smil import make_smil

        # LOGGER.info(self.config)
        # Note: this filename is based on user's text file path.
        save_filename = self.config.get("filename", "output")
        tokenized_xml_path = os.path.join(self.config["output_base"],
                                          save_filename + ".xml")
        audio_extension = self.config["audiofile"].split(".")[-1]
        audio_path = os.path.join(self.config["output_base"],
                                  save_filename + "." + audio_extension)
        smil = make_smil(os.path.basename(tokenized_xml_path),
                         os.path.basename(audio_path), results)

        smil_path = os.path.join(self.config["output_base"],
                                 save_filename + ".smil")
        save_xml(tokenized_xml_path, results["tokenized"])

        import shutil

        shutil.copy(self.config["audiofile"], audio_path)

        save_txt(smil_path, smil)
        save_minimal_index_html(
            os.path.join(self.config["output_base"], "index.html"),
            os.path.basename(tokenized_xml_path),
            os.path.basename(smil_path),
            os.path.basename(audio_path),
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

    # def tokenize(self):
    #     from lxml import etree
    #     from readalongs.text.tokenize_xml import tokenize_xml

    #     if not self.config.get("tokfile"):
    #         self.config["tokfile"] = self.config["xmlfile"].replace("prep", "tok")
    #     xml = etree.parse(self.config["xmlfile"]).getroot()
    #     xml = tokenize_xml(xml)
    #     save_xml(self.config["tokfile"], xml)

    # def g2p(self):
    #     import io
    #     from lxml import etree

    #     g2p_kwargs = {
    #         "tokfile": io.BufferedReader(io.FileIO(self.config["tokfile"])),
    #         "g2pfile": self.config["xmlfile"].replace("prep", "g2p"),
    #         "g2p_fallback": None,
    #         "force_overwrite": True,
    #         "g2p_verbose": False,
    #         "debug": False,
    #     }
    #     g2p_xml = etree.parse(g2p_kwargs["tokfile"]).getroot()
    #     from readalongs.text.add_ids_to_xml import add_ids

    #     g2p_xml = add_ids(g2p_xml)
    #     from readalongs.text.convert_xml import convert_xml
    #     from readalongs.util import parse_g2p_fallback

    #     g2p_xml, valid = convert_xml(
    #         g2p_xml,
    #         g2p_fallbacks=parse_g2p_fallback(g2p_kwargs["g2p_fallback"]),
    #         verbose_warnings=g2p_kwargs["g2p_verbose"],
    #     )
    #     from readalongs.text.util import save_xml

    #     save_xml(g2p_kwargs["g2pfile"], g2p_xml)


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
