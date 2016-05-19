from flask import Flask, render_template, redirect, request
from SpotifyTest import *
import copy



player = SpotifyPlayer()
player.run_player()
#current_song='none'
app = Flask(__name__)
queuelist = ['q', 'Q', 'queue', 'Queue']
playlistlist = ['p', '$', 'playlists', 'Playlists']

class info():
    def __init__(self):
        self.current_song='none'
        self.type = 'song'
        self.results=[]

    def refresh(self):
        #print current_song
        print 'type:', self.type
        if player.track == 'none':
            self.current_song = 'none'
        else:
            self.current_song = player.track.name
        return render_template('index.html', title='test', song=self.current_song, results=self.results, res_type=self.type)

make = info()

@app.route('/')
def run_app():
    return make.refresh()

'''
@app.route('/yield')
def index():
    def inner():
        for x in range(1000):
            time.sleep(1)
            yield '%s<br/>\n' % x
    return Response(inner(), mimetype='text/html')
'''

@app.route('/vol', methods=['POST'])
def changevol():
    direction = int(request.form['vol'])
    player.volume(direction)
    return redirect('/')

@app.route('/play', methods=['POST'])
def play():
    player.play()
    #make.current_song = player.track.name
    return redirect('/')

@app.route('/pause', methods=['POST'])
def pause():
    player.pause()
    return redirect('/')

@app.route('/skip', methods=['POST'])
def skip():
    player.next_song()
    #make.current_song = player.track.name
    return redirect('/')

@app.route('/', methods=['POST'])
def search(search=''):
    if search == '':
        search = request.form['text']
    results=[]
    if search in playlistlist:
        print 'looking in playlists'
        make.type = 'playlist'
        results = list(player.session.playlist_container)
        print 'got result'
        player.add = True
    elif search in queuelist:
        make.type = 'song'
        results = player.queue[0:player.queue_index]
        player.add = False
        print 'set add to False'    
    elif search != '':
        make.type = 'song'
        player.add = True
        print 'set add to true'
        results = copy.copy(player.search(search))
    make.results=results
    return redirect('/')

@app.route('/back', methods=['POST'])
def back():
    player.last_song()
    #make.current_song = player.track.name
    return redirect('/')

@app.route('/queue', methods=['POST'])
def queue():
    song = str(request.form['song']).split("'")
    if make.type == 'playlist':
        print 'here'
        playlist = player.session.get_playlist(song[1])
        print 'got playlist'
        playlist.load()
        print 'loaded playlist'
        [player.queue.insert(player.queue_index, track) for track in playlist.tracks]
        return search('q')
    track = player.session.get_track(song[1])
    print player.add
    if player.add:
        print 'queued song'
        player.queue.insert(player.queue_index, track)
        player.queue_index += 1
    else:
        print 'removed song'
        rm_song(track)
    return search('q')



def rm_song(song):
    print 'removing song'
    player.queue.reverse()
    player.queue.remove(song)
    player.queue.reverse()
    player.queue_index -= 1
    return redirect('/')

@app.route('/playnow', methods=['POST'])
def playnow():
    song = str(request.form['song']).split("'")
    if make.type == 'playlist':
        playlist = str(request.form['song']).split("'")
        playlist = player.session.get_playlist(playlist[1])
        playlist.load()
        [player.queue.insert(0, track) for track in playlist.tracks]
        return search('q')
    track = player.session.get_track(song[1])
    if not player.add:
        rm_song(track)
    print 'playing song'
    player.queue.insert(0, track)
    player.queue_index += 1
    return search('q')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)