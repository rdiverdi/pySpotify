import spotify
import threading
import time
import copy
import random
import alsaaudio

queuelist = ['q', 'Q', 'queue', 'Queue']
playlistlist = ['p', '$', 'playlists', 'Playlists']

class SpotifyPlayer():
    def __init__(self):
        self.logged_in_event = threading.Event()
        self.queue = []
        self.queue_index = 0
        self.played = []
        self.track = 'none'
        self.m = alsaaudio.Mixer('PCM')
        self.vol = self.m.getvolume()[0]

        self.add = True

    def volume(self, direction):
        self.vol = self.m.getvolume()[0]
        new_vol = self.vol + 10*direction
        if new_vol < 0:
            new_vol = 0
        elif new_vol > 100:
            self.vol = new_vol
        print self.vol
        self.m.setvolume(new_vol)

    def is_loggedin(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    def is_song_end(self, session):
        self.next_song()

    def next_song(self):
        if self.queue == []:
            self.queue = copy.copy(self.played)
        self.track = self.queue.pop(0)
        self.play_song(self.track)

    def last_song(self):
        self.track = self.played.pop(-2)
        self.queue.insert(0, self.played.pop(-1))
        self.play_song(self.track)

    def play_song(self, track):
        print track.name
        track.load(timeout=5)
        #self.session.player.prefetch(track)
        self.session.player.load(track)
	time.sleep(2)
        self.session.player.play()
        if self.queue_index > 0:
            self.queue_index -= 1
        self.played.append(track)
	try:
	    self.queue[0].load()
	    self.session.player.prefetch(self.queue[0])
	except:
            pass

    def pause(self):
        self.session.player.pause()

    def play(self):
        if self.session.player.state == 'unloaded':
            self.next_song()
        else:
            self.session.player.play()

    def search(self, search):
        print 'searching for %s' %search
        results = self.session.search(search)
        print results
        results.load()
        return results.tracks

    def run_player(self):
        login = open('login.txt', 'r') #login.txt should be your login with username on the top line and password next
        credentials = login.read().split('\n')
        self.session = spotify.Session()
        self.session.set_cache_size(3000)
        spotify.preferred_bitrate(self.session, 96)
        audio = spotify.AlsaSink(self.session)
        loop = spotify.EventLoop(self.session)
        loop.start()
        self.session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, self.is_loggedin)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self.is_song_end)
        self.session.login(credentials[0], credentials[1])
        self.logged_in_event.wait()
        print 'waiting'

        print 'logged in'
	try:
	    playlist = self.session.playlist_container[-1]
        except:
            time.sleep(2)
            playlist = self.session.playlist_container[-1]
        playlist.load()
        self.queue = [track for track in playlist.tracks]
        random.shuffle(self.queue)

from Tkinter import *

class SpotifyWidgit():
    def __init__(self):
        self.setup_window()

    def set_quit_flag(self):
        self.window.quit_flag = True

    def setup_window(self):
        self.setup_base_window()
        self.player = SpotifyPlayer()
        self.cur_song = StringVar()
        self.setup_buttons()
        self.setup_search()

    def setup_base_window(self):
        self.window = Tk()
        self.window.minsize(width=200, height=50)
        self.window.configure(bg='#444444')
        self.window.geometry('200x35-100+100')
        setattr(self.window, 'quit_flag', False)
        self.window.protocol('WM_DELETE_WINDOW', self.set_quit_flag)
        self.window.after(0, func=self.loop)
        self.window.wm_attributes('-topmost',1)

    def setup_buttons(self):
        self.button_bar = Frame(self.window, bg='#444444')
        self.button_bar.pack(fill='x', side=BOTTOM)

        self.song_name = Label(self.window, bg='#444444', textvariable=self.cur_song)
        self.song_name.pack(fill='x', side=BOTTOM)

        self.next_song = Button(self.button_bar, text='>|', command=self.player.next_song)
        self.next_song.configure(bg='#608913', highlightbackground='#81b71a', activebackground='#81b71a')
        self.last_song = Button(self.button_bar, text='|<', command=self.player.last_song,bg='#608913')
        self.last_song.configure(bg='#608913', highlightbackground='#81b71a', activebackground='#81b71a')
        self.pause = Button(self.button_bar, text='ll', bg='#608913', command=self.player.pause)
        self.pause.configure(bg='#608913', highlightbackground='#81b71a', activebackground='#81b71a')
        self.play = Button(self.button_bar, text='>',bg='#608913', command=self.player.play)
        self.play.configure(bg='#608913', highlightbackground='#81b71a', activebackground='#81b71a')

    def setup_search(self):
        self.search_window = Frame(self.window, bg='#444444')
        self.search_window.pack(fill='x', side=TOP)
        self.num_songs = []

        self.search_bar=Entry(self.search_window, bg='#666666')
        self.search_bar.insert(0, 'search')
        self.search_bar.bind("<Button-1>", self.rm_text)
        self.search_bar.pack()
        self.space=Frame(self.search_window, bg='#444444', height=15)
        self.space.pack()

        self.search_bar.bind('<Return>', self.search)

    def search(self, event):
        result = []
        search = self.search_bar.get()
        if search in playlistlist:
            result = self.player.session.playlist_container
            self.setup_search_result(result, 'playlists')
        elif search in queuelist:
            result = self.player.queue[0:self.player.queue_index]
            self.setup_search_result(result, 'songs')
        elif search != '':
            result = self.player.search(search) #run search
            self.setup_search_result(result, 'songs')

    def setup_search_result(self, result, what):
        if len(self.num_songs) > 0:
            self.results.destroy()
        self.num_songs = range(len(result))

        #setup result window
        self.results = Frame(self.search_window)
        self.results.configure(bg='#444444')
        self.results.pack(fill=BOTH)
        self.grid = Frame(self.results, bg='#444444')
        columns=4
        if len(result)>0:
            self.grid.grid(row=0, column=0, rowspan=len(result), columnspan=columns, sticky='nsew')

            #fill result window
            for i in self.num_songs:
                result_line(i, result[i], what, self)

    def queue(self, track):
        print 'queued song'
        self.player.queue.insert(self.player.queue_index, track)
        self.player.queue_index += 1

    def play_now(self, track):
        print 'playing song'
        self.player.queue.insert(0, track)
        self.player.queue_index += 1

    def queue_playlist(self, playlist):
        print 'queued playlist'
        playlist.load()
        [self.player.queue.insert(self.player.queue_index, track) for track in playlist.tracks]

    def play_now_playlist(self, playlist):
        playlist.load()
        [self.player.queue.insert(0, track) for track in playlist.tracks]

    def rm_text(self, event):
        self.search_bar.delete(0, END)

    def setup(self):
        self.player.run_player()
        self.initGUI()

    def run(self):
        self.window.mainloop()

    def update_cur_song(self):
        if self.player.track == 'none':
            self.cur_song.set('none')
        else:
            self.cur_song.set(self.player.track.name)

    def initGUI(self):
        self.window.title('Spotify')
        self.next_song.pack(side=RIGHT, padx=5, pady=5)
        self.play.pack(side=RIGHT, padx=5, pady=5)
        self.pause.pack(side=RIGHT, padx=5, pady=5)
        self.last_song.pack(side=RIGHT, padx=5, pady=5)

    def loop(self):
        if self.window.quit_flag:
            self.window.destroy()  # this avoids the update event being in limbo
        else:
            self.update_cur_song()
            self.window.after(10, func=self.loop)

class result_line():
    def __init__(self, index, track, what, parent):
        self.parent=parent
        self.i=index
        self.track=track
        if what == 'songs':
            self.make_line_song(self.parent.grid)
        elif what == 'playlists':
            self.make_line_playlist(self.parent.grid)
    def make_line_song(self, grid):
        play_now = Button(grid, text='>', bg='#444444', command=lambda: self.parent.play_now(self.track))
        play_now.grid(row=self.i, column=0, sticky='nsew')
        title = Button(grid, text=self.track.name, bg='#444444', command=lambda: self.parent.queue(self.track))
        title.grid(row=self.i, column=1, sticky='nsew')
        artist = Button(grid, text=self.track.artists[0].name, bg='#444444', command=lambda: self.parent.queue(result[i]))
        artist.grid(row=self.i, column=2, sticky='nsew')
        track_millis = self.track.duration/1000
        track_time = '%d:%02d' %(track_millis/60, track_millis%60)
        time = Button(grid, text=track_time, bg='#444444', command=lambda: self.parent.queue(self.track))
        time.grid(row=self.i, column=3, sticky='nsew')
    def make_line_playlist(self, grid):
        play_now = Button(grid, text='>', bg='#444444', command=lambda: self.parent.play_now_playlist(self.track))
        play_now.grid(row=self.i, column=0, sticky='nsew')
        title = Button(grid, text=self.track.name, bg='#444444', command=lambda: self.parent.queue_playlist(self.track))
        title.grid(row=self.i, column=1, sticky='nsew')
        #artist = Button(grid, text=self.track.artists[0].name, bg='#444444', command=lambda: self.parent.queue(result[i]))
        #artist.grid(row=self.i, column=2, sticky='nsew')
        #track_millis = self.track.duration/1000
        #track_time = '%d:%02d' %(track_millis/60, track_millis%60)
        #time = Button(grid, text=track_time, bg='#444444', command=lambda: self.parent.queue(self.track))
        #time.grid(row=self.i, column=3, sticky='nsew')






if __name__ == '__main__':
    window = SpotifyWidgit()
    window.setup()
    window.run()
