# Pinewood Derby 2023
- [Introduction](#introduction)
- [The Why](#the-why)
  - [The 2021 Event](#the-2021-event)
  - [The 2022 Event](#the-2022-event)
  - [Room for Improvement](#room-for-improvement)
- [Design](#design)
  - [The Finish Line](#the-finish-line)
  - [The Start](#the-start)
  - [The Tournament](#the-tournament)
  - [Hardware](#hardware)
  - [Web Interface](#web-interface)
  - [Using a Timed System](#using-a-timed-system)
  - [Conclusion](#conclusion)
- [Bumps and Bruises](#bumps-and-bruises)
- [How-To](#how-to)
  - [Hardware](#hardware)
  - [Connecting to the Network](#connecting-to-the-network)
  - [Firewall](#firewall)
  - [Software](#software)
    - [What you need](#what-you-need)
    - [Preparing the Backend](#preparing-the-backend)
    - [OBS](#obs)
    - [Populating the Racer List](#populating-the-racer-list)
    - [Starting the Backend](#starting-the-backend)
    - [The Web UIs](#the-web-uis)
  - [Running an Event](#running-an-event)
    - [Starting](#starting)
    - [Advanced Control Panel Usage](#advanced-control-panel-usage)
      - [Race Data](#race-data)
      - [Race Management](#race-management)
      - [OBS Controls](#obs-controls)
      - [Miscellaneous](#miscellaneous)
    - [The Other Panels](#the-other-panels)
- [Closing Words](#closing-words)


<div style="page-break-after: always;"></div>

## Introduction
Welcome! This repository contains just about everything you need to know to run a Pinewood Derby event, at least in the way I and my group did in 2023. Note that this entire system is designed with [this track](https://derbymagic.com/product/all-things-2-lane/) in mind (2 lanes with a starting lever). In fact, this system is designed with extremely specific circumstances, but feel free to modify things to your own needs. You might find a stepper motor or some solenoids would work better for starting the cars off, or if you have more than 2 lanes, consider using infrared modules to detect motion. Note this will require a lot of code modification, but hopefully this document will help provide some building blocks in the design process.

As a quick word of caution, **this was not designed for beginners**. If you don't know anything about electronics or programming, I suggest you look elsewhere. This repository is an amalgamation of different technologies and is not friendly in a lot of ways. However, if you're one of the few who go through all of this and build the structures and acquire and wire up the hardware, then you'll definitely be interested in the `How To` section below.

All of the code and hardware enables the following:
- Automatic starting via a motor
- A relatively robust timer system to display racer times and positions
- A mixed tournament system designed to handle at least 60 players in under 2h 30m, while allowing a minimum of 3 races for every player.
- Three different web interfaces for race management:
    - One for the controller to manage the entire event from
    - One for the emcee to be able to read relevant event data
    - One for players to check if they've been eliminated or not 
- An OBS handler to allow showing event info to the audience in a controlled way

<div style="page-break-after: always;"></div>

## The Why
The event we ran in 2023 was not the first Pinewood Derby event we've run. However, I didn't start helping with event management until 2021. To help rationalize why this is as complicated as it is, I'll go through both of the 2021 and 2022 events and explain how they worked and what issues they had.

### The 2021 Event
This event was a bit more old school. I used my mom's Nikon camera with some drivers so it's POV could be recorded with OBS, and that was used for any instant replays. The tournament itself was double-elimination style done on paper by one of the members of our group. As such, there were delays with getting who was next, who was up after that, and it wasn't as streamlined as it could have been.

So putting all of that together, the event ran like this:
- I would give a thumbs up to the person at the start of the track who was responsible for pulling the lever, the cars would set off, and I would start my recording. 
- The winner would be recorded and sent to the person responsible for managing the tournament on paper, and he would tell the emcee who was up next.
- Repeat until the tournament was over.

But this posed a number of problems:
- Figuring out who was up next put a lot of pressure on the person managing the tournament board, and it wasn't always feasible. 
- There were some communication issues where cars were started when I wasn't ready to record.
- The recording quality was trash, partly due to me not having a steady hand.

### The 2022 Event
I took on a lot more responsibilities this year. Including the prior year's duties of camera / instant replay management, I was also in charge of managing the tournament board itself. Since I don't have 6 arms, I chose to look for technological means of managing all this. My search led me to this amazing piece of software: [bp5000 by isaiahr](https://github.com/isaiahr/bp5000). I still had to enter all the winners manually, but the interface was easy to use, and I was able to focus on automating other parts. Instead of using the monitor to exclusively display the camera feed (which was also improved by getting a webcam and mounting it to a tripod; much more sturdy than holding it myself), it also displayed who was currently racing and who was up next. I also had a number of different scenes in OBS (one for the camera feed with the racing info, one to show the tournament bracket, and one to show the video playback, which was hacked together using [python-vlc's Qt example](https://github.com/oaubert/python-vlc/blob/master/examples/pyqt5vlc.py) that I found on GitHub). I used an IR receiver, an Uno, and a remote so that I could automate it further. 

Putting it all together, I had:
- A remote which could either toggle recording or change the scene displayed on screen
- A GUI program to manage the tournament
- A terminal window which I used to update the "Now Racing" and "Up Next" text
- A camera, pointed at the end of the track to capture video. 

While it was an improvement over last year, it was not without flaw. Some of those include:
- I spent the entirety of the 3 hours the event ran for hunched over a computer with a remote. 
- There were a number of communication errors between myself and the person who was at the start of the track pulling the lever. This led to the cars starting without me being ready and a few recordings were missed because of this. 
- While seeing who was currently racing and who was up next was far better than last year's event, the emcee still had to glare across the entire room to make his announcements.
- With 50 racers and a double elimination tournament, the event ran far longer than originally intended. I also messed up how I ran the tournament and did the entire winners bracket at once, then all of the losers bracket, which led to basically knowing who won halfway through. 

### Room for Improvement
So now, with the 2023 event approaching and having too much time on my hands, I set out to fix as many as of these issues as I could.
As a summary:
- Double-elimination tournaments are great, but not when you have 50 players and want to keep it as close to 2 hours as possible. 
- My spine did NOT appreciate this event, and I don't have that great of posture to begin with.
- The emcee needed a better way to get event info rather than squinting across a large room.
- I wanted to cut down on the communication errors between the track start attendant and myself by ensuring both parties were ready.
- I was itching to use my developing interest in hardware.
- There weren't many close calls, but when there were, the camera was **not** a good way of definitively checking who won.
- The track we were using had one lane which was noticeably faster than the other lane. Since race winners were determined in a best of 3, there were situations where you won only because you started on the faster lane.
- The remote control system for automation worked, but there was certainly room for improvement.

With these goals, I came up with the following ideas:
- Find some hardware based solution to more accurately determine the winner.
- Use some mechanism at the start of the track to automatically start the lever.
- Think of a new tournament format to make the event go a little quicker, especially with more racers.
- Create a better interface between myself and the various programs, which will save both sanity and spine. 

<div style="page-break-after: always;"></div>

## Design
### The Finish Line
I began with the first issue. Originally, I was thinking of using ultrasonic sensors (which use ultrasonic waves to measure distance to an object), however, after some googling, I found that these aren't as reliable at close range. After some digging, I had the idea of using lasers. I was originally planning to mount the laser receivers in the center of the track, with the emitters on the outside. After hours and hours of thinking, I finally had the idea to mount a thin mirror in the middle and have both the emitters and receivers on the outside (I used a hard drive platter from a drive I'd taken apart years prior).

### The Start
Next, I turned to the start of the track. Originally, I thought of using a stepper motor that I had on hand to manually turn the spring-loaded lever-activated stoppers. However, this motor was heavy, and I didn't have constant access to the track start, so I decided to look elsewhere solely because I didn't want to design something to hold all the hardware up. Instead, I had the idea of using a much lighter servo motor to push the lever as if it were a finger. This would still require someone at the start of the track to set the lever in place, but some code and some buttons to make sure myself and the attendant were ready would mean only a small platform (I originally thought a table) would be needed to hold everything.

### The Tournament
Next, I looked into new tournament formats. My search didn't last long, as I found the Swiss tournament format. This format offers numerous improvements over double-elimination:
- Players can be given as many guaranteed races as you'd like, instead of just the two that the double-elimination provided. 
- Players are matched up with other players of similar skill levels as the event moves on, rather than being swiftly eliminated due to bad luck when being paired.
- Swiss doesn't explicitly eliminate players, so the event length can be fine tuned with a custom elimination system. 

For those of you who might be confused, here's how the Swiss tournament works (or at least how it's applied here):
- At the start, every player has a score of 0, and every round consists of players being paired up with another player.
- If a player wins a race, they get 1 point. If they lose, they get 0. 
- When a new round is queued, players are matched up with players of similar scores, so a player who has lost all their races has the opportunity to climb back up by beating other players who have also lost all their racers. Similarly, players who are doing better have a bigger challenge as they are paired up with players who are also doing well.

I didn't want to write my own library to handle a Swiss tournament, but luckily I found a shining light in the darkness (thanks once again to the open source community): [pypair by Jeff Hoogland](https://github.com/JeffHoogland/pypair). 
By experimenting with this library and an assumed 60 players, I was able to find that if we used 3 qualifier rounds for players to build up their score, and then every round after that, we eliminated everyone under the median of all the scores, I was able to reduce the 60 players to 7-12 racers in under 8 rounds. Assuming 30 seconds per run, the swiss part of the tournament would take just over 2 hours (approximately 2h and 25m to be not-so-exact). Then, for suspense and to make the end of the event go a little quicker, I chose to just put the remaining players after these phases of elimination into a single-elimination tournament to determine the winner.

At the end of it all, the tournament goes like this:
- Players get 2 qualifier rounds to set their starting score for the event. This will allow them to be paired up with players of similar skill levels.
- At the end of Round 3, everyone below the median score of all players will be eliminated. For 60 players, I found that it eliminates 15.
- This continues until either
    - 12 or fewer players are left
    - The round counter has exceeded 8
- After this point, every remaining player will be put into a single elimination tournament, where the last player standing wins.

### Hardware
And then I turned to the question of how I'd actually handle the data between the motor at the start of the track and the lasers at the end. 
I first thought of what would actually be processing or sending the signals. I had an Arduino Uno on hand, but the idea of several wires strewn across the room didn't appeal to me. I had heard of ESP32's before (which are like the Uno in that it's open-source hardware, but these are smaller and WiFi capable), so I decided to purchase some from AliExpress and try them out. 
At first, I began with ESP-NOW. When that failed, I spent quite some time getting an Access Point to work (basically a router). Once I learned how to do this, it seemed to be the clear winner with how the different parts would communicate. 

### Web Interface
Then, I turned to the question of a new interface. Originally, I had bought a keypad (0-9, *, #, and A-D buttons). In my mind, the A-D would select modes, the keypad could be used for input, and the `*` and `#` buttons could do whatever I needed. However, when actually planning out what buttons would do what, it quickly became a mess. And then I realized that I could just host a web UI off of a laptop connected to the network, which would also allow for easier accessibility for the emcee. Luckily, I had some spare iPads so the laptop could be free to manage everything else in the backend (now an OBS menu, a video player, a tournament board, and communicating with the hardware parts).

### Using a Timed System
Now that I had a better idea of the interface and hardware I was going to use, there was one last thing I needed to address: one lane being faster. Eventually, the idea came to me to use a best time system rather than a best of 3. Basically, each car runs in each lane once, and the fastest overall time is the winner. This also brings the event closer to the ideal 2 hour mark, as we can eliminate a run altogether. To supplement this, I chose to use 7-segment displays above each lane to display the time. Originally, I was going to display run and race times (race time is the sum of all run times), however, since the cars switch lanes, it meant that the race time would need to as well, so I made the decision to instead display position and run times, and have the backend manage everything to do with full races. Keeping the timer and laser system free of any unneeded context made developing it far simpler. Because we're using a motor to start the cars, it can also have a dual purpose of measuring when the cars started.

### Conclusion
So now, in the abstract, here's a list of all the parts that work to run this event:
- A laptop running a web server to host a web page for the emcee and a control panel for me
- The same laptop is also running the backend which controls OBS, the tournament, the video player, and acts as the communication hub between all the hardware modules
- An ESP32 running code to serve as an access point, allowing everything to talk to each other
- An ESP32 responsible for managing the laser receivers and position and time displays
- An ESP32 responsible controlling the motor

You can find schematics for all the hardware components in this repository.

<div style="page-break-after: always;"></div>

## Bumps and Bruises
Rather than discuss everything in detail, I'm just going to make a long list of all the various issues I encountered when developing this.
- Getting the ESP32's to talk to each other was exceptionally painful. I spent hours and hours trying to get ESP-NOW to work, and when I gave up, I spent hours and hours trying to get a library to manage the access point working. And then I spent more hours getting them to actually send GET requests.
- After ordering some raw 7-segment displays (12 pin version), I spent an entire day trying to figure those out. Those displays were returned and I ordered some TM1637 modules instead (bootleg I2C, CLK and DIO pins for data and then a 5V and GND pin instead of 12 for uhhh... well explaining them would take too long).
- Writing a mini-library to handle the TM1637 displays took ages, and so much debugging. Designing the library to use hardware interrupts for the laser receivers also took a while to work around. My original implementation had the interrupt call a function on the class, but that failed since the interrupts have to call a completely void function, and class methods always implicitly take in `this`. It also took a while to figure out that I needed to include a header to make them support `std::function` rather than a basic function pointer, meaning it could accept lambdas. 
- Switching the race display to functioning as a position display took far longer than it should've.
- It took so long to figure out how to mount the lasers so they could fit on the track. I measured less than an inch in-between lanes that I had to work with. 
- I spent at least 3 days figuring out why the laser receivers didn't work reliably. I ended up learning that they have an internal pull down resistor, and that they are very sensitive to light. As it turns out, the table next to the window that they sitting on gets enough sunlight to block the receivers. To mitigate this, I hot glued small cardboard "houses" that sit over the receivers to block most of any ambient light.
- There were at least 4 different instances where something didn't work because I forgot to hook up a common ground. 
- One of the first things I did in terms of the backend was create a basic script to simulate pypair usage. I used this to create a single class that handled both the single elimination tourney and the swiss tourney. After spending about 12 hours doing that one day, I eventually gave up and rewrote the tournament system to use two separate classes. This worked nearly on the first try with a few miscellaneous bugs (such as learning that you need to spend the first round of a single elimination tourney narrowing the player list to be a power of 2).
- The sheet quantity of endpoints across all the various codebases is enough to make me nervous, and I wrote them. 
- Surprisingly, the motor board is the part that gave me the least amount of trouble. Although, there was one hiccup. Originally the control panel started the cars directly after the attendant pressed a button to indicate the cars were set up. However, one kid mentioned to me as I was talking to some people about that system that one of the best parts of a race was getting to start the lever yourself after the attended did what they needed. After hearing that, I felt obligated to pass off the actual starting process to the attendant, with the controller only having to give approval. 
- I originally forgot to account for the cars switching lanes every other run, which meant that all times on the left lane were counted for racer 1. This even almost made it into production, with me remembering it at about 11:30 PM when I was going to bed a week before the big day. 
- Tweaking the CSS to display right for both my laptop and the iPads was another pain. I also had `style` attributes on way too many HTML nodes before I cleaned up my internal CSS.
- I had to add a system to both the timer board and the motor board to reboot themselves if they lost connection (it checks every second). I found out things could go south VERY quickly if they lost connection in the middle of a race. I also had to add an endpoint to change the IP they tried to connect to, including a 10 second grace period on startup where they won't reboot if they couldn't connect.
- Figuring out to organize the cluster of endpoints just in the backend took longer than it should have (thank you blueprints).
- Moving the code so that it could work on my laptop (after I did all the primary development on my desktop) took several hours. The biggest hiccup was installing the PlatformIO extensions on the laptop so I could re-flash the boards if needed, except VSCode kept refusing to connect. It turns out I left some DNS settings where it was requesting a static IP on my home network that VSCode did not like. 
- Designing the actual structure to hold the timer and AP board and the motor board took **numerous** iterations. I'm extremely grateful to have someone who was knowledgeable enough to implement and accommodating enough to support my crazy ideas. Basically, my original design was NOT structurally stable. 
- Originally, the "toes" of my structure was going to use hot glue to secure the laser emitters and receivers in place. This quickly revealed itself to be a terrible idea.
After I had glued the modules to match a specific mirror position, I found out I bumped the mirror in-between gluing each side. This meant I had to cut one side up, which resulted in some ruined paint. After having to manipulate the height of the mirror platform using some small pieces of dowels, this meant the bottom of the mirror was pressed up against a bump in the end of the track, which made it even easier to move accidentally. Eventually, I cut off all the hot glue and instead used some clay to mount the modules. It was slightly pliable at room temperature, but it allowed for small adjustments to be made while being semi-permanent. 
- The video player, no offense, is kind of a piece of junk. Well, it's not really the fault of any developer, it's just that the UI library it uses (Qt) is very much not designed to do what I was trying to make it do (run in a non-main thread and be controlled remotely). Making it crash was very easy, and if it crashed, it would bring down the entire program. So instead, I had to make it run as its own process so that if it died, it wouldn't sink the entire ship. Making it its own thread while allowing it to communicate with the main backend took some effort. Pro Tip: Don't try to automate Qt based UIs. Maybe next year I'll use `tkinter` or something.
- Trying to optimize the time a network call took on the ESPs was a fruitless task, so I instead just chose to make them wait some time before sending the signal that a lane finished. I'll just copy from the comments of the timer module:

*It used to work so that the display would instantly show the time and position when the laser was tripped. However, this caused about a 47 to 49 millisecond delay between when the laser trip body was entered and when it was exited. (That's without the network request to tell the backend about the finish!) This means that even if the cars finished within like 2 milliseconds of each other, it would show at least a 47-49 millisecond gap between them.
So, instead, the heavy stuff is offloaded to be 0.1 seconds after the actual trip. After 100 milliseconds has passed, we can accept another 50 millisecond inaccuracy since it's not really a close call anyway.*

- Tweaking how the tournament operated to get as close to the 2 hour mark as possible took a lot of thinking too. I ended up just chopping off an entire qualifier round which shaved off nearly 30 minutes.
- Apparently Android **really** doesn't like accessing LAN based webpages, hence why iPads are used and not my Samsung phone.

Basically, I ran into a lot of issues, but I got myself into this mess, and thankfully I got myself out of it. 
I also figure any audience might also enjoy a list of things that didn't get used (some of which have been mentioned previously):
- I experimented with using the flask backend for hosting the web pages.
- The TM1637 modules used to be powered with a buck driver since I was under the impression that the ESP32's could not handle 5V. This turned out to be false, which is why there's still a blue cube next to the breadboard in the blender model I made. I also bought some logic level shifters, which turned out to not really work.
- I bothered to do a power audit on everything despite already ordering some PSU's capable of delivering 3 amps. If the relatively simple circuitry drew over 3 amps, then there's a different problem.
- I experimented with using both [pynecone](https://github.com/pynecone-io/pynecone) and making an android app using [Kivy](https://github.com/kivy/buildozer) instead of a webpage. Pynecone wouldn't load on my older iPad (iOS 12), and Kivy was too much work considering the web UI was basically done by then.
- I originally considered using something like MariaDB before I discovered TinyDB. 
- The original end of track structure was designed in [Blockbench](https://github.com/JannisX11/blockbench) (which is designed for Minecraft) before I switched to blender.

<div style="page-break-after: always;"></div>

## How-To
Well, I suppose you're probably bored of reading about my design process (if you even read it at all). In any case, if you happen to be one of the few who already have the needed structures on hand (AKA you know me personally and I'm not available to run a derby), then the section below is for you. I should note I'm assuming you're using Windows 10.

### Hardware
You'll need to handle acquiring the hardware and supporting structures yourself. If you haven't yet, you can find electrical schematics to wire everything up as needed (which also provides a rough list of parts). The boards need to be preprogrammed with the relevant code, so make sure you have ESP32-CH9102X drivers installed for that. Then, you can use the supplied PlatformIO files to re-flash the boards. For the structures, you can use the blender file in this repository as reference for the structure that holds the timers and lasers. For the motor structure, you're mostly on your own. I had an extremely gifted friend create a contraption that holds the motor in place so it doesn't spin out that just attaches to the track start using some holes that he drilled. The sticky stuff on the bottom of most breadboards will be your friend here; you don't want someone accidentally knocking it off!

### Connecting to the Network
In my system, the timer board and the AP board had a shared power supply, so step one is to supply power to the AP board. Connect your laptop to the access point, using `PiD-AP` as the network name and `longleggedducks` for the password. In Control Panel, go to `Network and Internet > Network and Sharing Center > Change Adapter Settings`. Right click the device that looks like it's used for your normal WiFi connections, and edit the properties (either right click to select and press `Change settings of this connection`). Select `Internet Protocol Version 4 (TCP/IPv4)` and select properties. Select `Use the following IP address`, and enter the following values (copy any existing values, as you'll want to reset these after the event is over. Otherwise, you may find your internet on your device is wonky):
- IP address: `192.168.132.106`
- Subnet mask: `255.255.255.0`
- Default gateway: `192.168.132.100`

Click OK, and close out of Control Panel. 

### Firewall 
Now, you need to configure your firewall so other devices can access the web interface and the backend. If you use a different antivirus other than Windows Defender, you're on your own.
Open `Windows Defender Firewall with Advanced Security`, click `Inbound Rules`, and then `New Rule`. Select `Port`, and on the next menu, select `TCP` and type in `80, 3000, 3001` for the ports. Choose `Allow the Connection`, and de-select `Domain` and `Public` on the next page. Enter whatever name and description you'd like, and click finish. Now, select this rule and click `Properties` on the right side. Under `Scope > Remote IP address`, select `These IP addresses`, then click `Add`. Select `This IP address range`, and type in `192.168.132.1` for `From` and `192.168.132.255` for `To`. Click OK, and close out of the firewall window. You're done here.

### Software
#### What you need
Now, you'll need to install all of the following:
- Python 3.10
- OBS 29
- VLC Media Player

#### Preparing the Backend
Once all that's installed, go into the supplied `backend` folder and open a terminal by typing `cmd` in the folder bar at the top. Type `py -m venv venv`, and then `venv\scripts\activate`. Then make sure there are no files name `SET_db.json`, `swiss_db.json`, or `ProgramData.json`. If there are, delete them. Create a file named `INIT` (no extension). 

#### OBS 
Start OBS and enable the websocket server under `Tools > WebSocket Server Settings`. Make sure it's enabled, disable authentication, make sure the port is `4455`. You'll also probably want to use `Scene Collection > Import` and `Scene_Collection_OBS.json` to setup the OBS scenes. Any extra OBS settings aren't hard to figure out. The big one is editing where the videos will be stored (`Settings > Output > Recording Path`). Just make sure when editing the camera that you only edit the `Basic Camera` scene. The `Advanced Camera` scene just duplicates this scene, so a change made in the basic view will also update in the advanced view. 

After running `main.py` Right click the left window in OBS and click `Fullscreen Projector` and then select the TV you have plugged in. You should notice the TV duplicates whatever scene you have set on the left. If it doesn't, make sure you have the TV marked as `Extend these displays` in your display settings.

#### Populating the Racer List
You need to edit `racer_list.txt` in the `backend` folder with your racer list. Put each name on a new line. You can also optionally edit `web-interface/scripts/elimination_check.js` to edit autocomplete settings for that page, but if it's not, just delete all the text between the first set of square brackets at the top of the file, so that it looks like this:
```js
const racerNames = [
];
```

#### Starting the Backend
Finally, run `py main.py` in your terminal to start the backend. 

#### The Web UIs
Open up a terminal in `web-interface` and run `start.bat` to start the web UIs. To view the UIs, make sure you're connected to the `PiD-AP` network and type `192.168.132.106` in the address bar to get to the main menu. There are 3 buttons on the main menu which will take you to the emcee panel, the control panel, and the elimination check panel.

Now's the time to power your motor board. From there, race management is relatively straight forward.

### Running an Event
#### Starting
To start the event, go to the control panel page and click `Next Round`. It will automatically start the first race for you. When you started the backend, it should've automatically set the OBS scene to `Custom Text` saying that the event will start soon. Make sure you switch the scene to `Advanced Camera` (the one you'll be using the most) after you start a round. From there, you're ready to run your event! 

#### Advanced Control Panel Usage
##### Race Data
This is the same info that the emcee panel has, but without the table or buttons. You can see who is up next, who is currently racing, how many players are left, and how many races are left in the current round. The table shows you the logged times for each of the races. You can use `Refresh` to populate the table if it isn't automatically done. If you want to manually add a race, use `Add Run`. The times displayed in this table are text fields, so you can edit them. Once you've made any edits, use `Update Race Data` to send it to the backend. It will also update the OBS scene, but not the hardware displays. You can also use the `Remove` button in the 3rd column for runs if you want to delete a run altogether.

##### Race Management
`Next Round` should only be used at the start of the event or when prompted by the control panel (this prompt appears when there are 0 races left in a round).

`Next Race` should only be used when there are at least 2 runs, but you can use it with 1 run. If you have 0 runs, then using it won't do anything (not even in the backend). If you try to use it less than 2 runs, it will ask you to confirm.

`Mark Start Ready` is what you'll normally use for motor control. When the track start attendant marks that the cars are set, this button will become enabled. Pressing it will inform the attendant that they are allowed to start. You can also use `Manually Start Motor` to act as if the attendant started the track. Using the Silent variation of this button will not inform the backend that a race has started. This will only spin the motor. 

The `Ignore Incoming Data From Timer` checkbox is useful if you want to let racers run their cars and use the timer system without running a tournament. The backend will still need to be running, but it won't update the OBS display or anything like that.

You can use the buttons under `Finish Controls` to mark a specific lane. Using the `Finish` buttons will act as if the car tripped the laser. Using `Fail` will display so on the timer hardware displays, and give the racer a 30 second penalty.

You can also edit the values on the display, whether or not the displays should automatically show when a lane is finished, and edit the visibility of values on the hardware displays. The `Auto Update Displays` checkbox pertains to editing the displays manually. When this is disabled, only the internal value will be changed, and you'll need to use the `Show ...` buttons to update the displays. The `Show Time On Finish` checkbox controls whether or not the position and time are automatically shown when a lane end is triggered. You can disable this if you want to create suspense.

##### OBS Controls
At the top, you can edit whether or not the camera should be recording. The `Auto Handle Recording` will make recording start 2 seconds after the motor is triggered, and stop as soon as both lanes have finished. I'd recommend leaving this on so you don't have to press `Toggle Recording` every single run. 

You can also set the scene (Video Playback is an alias for Fullscreen by the way), and trigger video player actions. Video Player actions will not function if a video player is not running, and even then they may not work (I mentioned in the Design section that it's volatile). Make sure one is open by using the `Open` and `Force Close` buttons at the top.

The `Round Complete Animation` buttons will be especially helpful at the end of a round. At the end of a round, if players have been eliminated and the mode is still swiss tournament, you will be prompted to play this animation. If it's taking too long to display all the names, you can use the `Skip` button to force it to skip to the end.

Finally, you can use the `Set Custom Text Card` field to display what's shown on the `Custom Text` scene. This can be useful to inform your audience that Single Elimination mode has begun, for example. 

##### Miscellaneous
The `Alert Emcee` field can be used to send an alert to the emcee. If you send an alert while another one is being displayed, it will overwrite it.

The `Blink` buttons are solely for debugging purposes and making sure that connections from the backend to the boards and the web UI and the boards are going through.

Finally, the `Force Close Video Player` and `Open New Video Player` are for the common instances where the Video Player doesn't behave. If it isn't responding, you can use these to kill it and try again.

#### The Other Panels
The Elimination Check panel is super straight forward. This can run on any device, but I just had it running on the laptop the backend was running on. If you decide to do this, get someone to watch over the laptop so a kid doesn't accidentally (or purposefully) ALT-F4 the derby into oblivion. Note that the autocomplete options here are set by the `racerNames` array at the top of `web-interface/scripts/elimination_check.js`, so if that matters to you (not everyone can spell Peter), set it there.

The emcee panel is also very simple. The only thing that it has that the controller panel doesn't is a button which will show a non-descriptive popup on the control panel informing the controller that the emcee is asking for assistance. 

## Closing Words
I hope this document has been helpful for you. Even if you aren't running a derby, you might find some of the things discussed applicable to other events. If you do run one, I wish you luck. Feel free to get in contact if you have any questions. For even more technical stuff, check out the API documentation to learn how all the parts talk to each other.

Special thank you to the following people:
* Jeff Hoogland, for creating pypair which was used to handle the majority of the swiss tournament stuff
* A special thank you to the one who built the structures for me. Couldn't have done it without you (name not included for privacy).
* Friends and family who supported me throughout the whole ordeal, and attended the event that all of this got used for
* Is it too cheesy to say "you" for viewing my work?
