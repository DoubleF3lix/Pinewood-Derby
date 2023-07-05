# Copied from https://github.com/oaubert/python-vlc/blob/master/examples/pyqt5vlc.py with modifications

import os

import vlc
from PyQt5 import QtCore, QtGui, QtWidgets

VIDEOS_DIR = "D:\\Videos"  # TODO change


class Player(QtWidgets.QMainWindow):
    def __init__(self, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Video Player")

        # Create a basic vlc instance
        # Only way to stop it from spamming the logs
        self.instance = vlc.Instance("--quiet")

        self.media = None

        # Create an empty vlc video player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()
        self.is_paused = False

    def create_ui(self):
        """Set up the user interface, signals & slots"""
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.openfilebutton = QtWidgets.QPushButton("Open File")
        self.hbuttonbox.addWidget(self.openfilebutton)
        self.openfilebutton.clicked.connect(self.open_file)

        self.openlastvideobutton = QtWidgets.QPushButton("Open Last Video")
        self.hbuttonbox.addWidget(self.openlastvideobutton)
        self.openlastvideobutton.clicked.connect(self.open_latest_video)

        self.playbutton = QtWidgets.QPushButton("Play/Pause")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        self.stopbutton = QtWidgets.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.nextframebutton = QtWidgets.QPushButton("Next Frame")
        self.hbuttonbox.addWidget(self.nextframebutton)
        self.nextframebutton.clicked.connect(self.next_frame)

        self.hbuttonbox.addStretch(1)
        self.playbackspeedslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.playbackspeedslider.setMinimum(1)
        self.playbackspeedslider.setMaximum(100)
        self.playbackspeedslider.setValue(100)
        self.playbackspeedslider.setToolTip("Playback Speed")
        self.hbuttonbox.addWidget(self.playbackspeedslider)
        self.playbackspeedslider.valueChanged.connect(self.set_playback_speed)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(100)
        # self.timer.timeout.connect(self.update_ui)

    def play_pause(self):
        """Toggle play/pause status"""
        if self.mediaplayer.is_playing():
            self.pause()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            # self.timer.start()
            self.is_paused = False

    def stop(self):
        """Stop player"""
        self.mediaplayer.stop()

    def next_frame(self):
        self.mediaplayer.next_frame()
        media_pos = int(
            self.mediaplayer.get_position() * 1000
        )
        self.positionslider.setValue(media_pos)

    def set_playback_speed(self, speed):
        if self.mediaplayer.is_playing():
            self.pause()
        speed /= 100
        self.mediaplayer.set_rate(speed)

    def pause(self):
        self.mediaplayer.pause()
        self.is_paused = True
        # self.timer.stop()

    def open_file(self):
        """Open a media file in a MediaPlayer"""

        dialog_txt = "Choose Media File"
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, dialog_txt, os.path.expanduser("~")
        )
        if not filename:
            return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])

        self.set_media()

    def open_latest_video(self):
        latest_video = self.get_newest_file_in_dir()
        self.media = self.instance.media_new(latest_video)
        self.set_media()

    def set_media(self):
        # Put the media in the video player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # The video player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        self.mediaplayer.set_hwnd(int(self.videoframe.winId()))

        self.play_pause()

    def get_newest_file_in_dir(self):
        paths = [
            os.path.join(VIDEOS_DIR, file_name) for file_name in os.listdir(VIDEOS_DIR)
        ]
        return max(paths, key=os.path.getctime)

    def set_position(self):
        """Set the movie position according to the position slider."""

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        # self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        # self.timer.start()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            # self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a video player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()
