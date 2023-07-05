# https://github.com/JeffHoogland/pypair
"""
This license applies to all files in this repository that do not have 
another license otherwise indicated.

Copyright (c) 2014, Jeff Hoogland
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
# Some modifications have been made by me


# User defined values
winPoints = 1
drawPoints = 0
byePoints = 1

import csv
import pickle
import random

# Load our library for building/working with graphs
import networkx as nx

# dbg = True
# debuglevel = 1


class Tournament:
    def __init__(self, startingTable=1):
        # Will hold all player data
        self.playersDict = {}
        # Current round for the event
        self.currentRound = 0
        # The next table we are going to assign paired players to
        self.openTable = 0
        # The starting table number
        self.startingTable = startingTable
        # Pairings for the current round
        self.roundPairings: dict[str, list[str, str]] = {}

        # this defines the max number of players in a network point range before we split it up. Lower the number, faster the calculations
        self.MaxGroup = 50

        # Contains lists of players sorted by how many points they currently have
        self.pointLists = {}

        # Contains a list of points in the event from high to low
        self.pointTotals = []

        # Contains the list of tables that haven't reported for the current round
        self.tablesOut = []

    def addPlayer(self, IDNumber, playerName, fixedSeating=False):

        """
        Holds player data that are in the event.

        Each player entry is a dictonary named by ID#

        ID : { Name:String,
                Opponents:List, Each entry is a ID number of someone you played
                Results:List, Each entry is a list of wins-losses-draws for the round
                Points:Int,
                OMW%:Float,
                Fixed Seating:Bool/Int, if False no fixed seating, if int that is the assigned table number}
        """

        self.playersDict[IDNumber] = {
            "name": playerName,
            "opponents": [],
            "results": [],
            "points": 0,
            "OMW%": 0.0,
            "fixed_seating": fixedSeating,
        }

    def loadPlayersCSV(self, pathToLoad):
        with open(pathToLoad) as csvfile:
            playerReader = csv.reader(csvfile, delimiter=",")
            for p in playerReader:
                # skip the row with headers
                if p[0] != "ID:":
                    if p[2]:
                        # Fixed seating is the third option
                        self.addPlayer(int(p[0]), p[1], int(p[2]))
                    else:
                        # If not present, leave it blank
                        self.addPlayer(int(p[0]), p[1])

    def loadEventData(self, pathToLoad):
        with open(pathToLoad, "wb") as outfile:
            self.playersDict = pickle.load(outfile)

    def saveEventData(self, pathToSave):
        with open(pathToSave, "wb") as outfile:
            pickle.dump(self.playersDict, outfile)

    def pairRound(self, forcePair=False):
        """
        Process overview:
            1.) Create lists of players with each point value
            2.) Create a list of all current points and sort from highest to lowest
            3.) Loop through each list of points and assign players opponents based with same points
            4.) Check for left over players and assign a pair down
        """
        if len(self.tablesOut) and not forcePair:
            # If there are still tables out and we haven't had a forced pairing, return the tables still "playing"
            return self.tablesOut
        self.currentRound += 1

        # Clear old round pairings
        self.roundPairings = {}
        self.openTable = self.startingTable

        # Contains lists of players sorted by how many points they currently have
        self.pointLists = pointLists = {}

        # Contains a list of points in the event from high to low
        self.pointTotals = pointTotals = []

        # Counts our groupings for each point amount
        self.countPoints = {}

        # Add all players to pointLists
        for player in self.playersDict:
            info = self.playersDict[player]
            # If this point amount isn't in the list, add it
            if f"{info['points']}_1" not in pointLists:
                pointLists[f"{info['points']}_1"] = []
                self.countPoints[info["points"]] = 1

                # Breakers the players into groups of their current points up to the max group allowed.
                # Smaller groups mean faster calculations
            if (
                len(pointLists[f"{info['points']}_{self.countPoints[info['points']]}"])
                > self.MaxGroup
            ):
                self.countPoints[info["points"]] += 1
                pointLists[f"{info['points']}_{self.countPoints[info['points']]}"] = []

                # Add our player to the correct group
            pointLists[f"{info['points']}_{self.countPoints[info['points']]}"].append(
                player
            )

            # Add all points in use to pointTotals
        pointTotals.extend(iter(pointLists))
        # Sort our point groups based on points
        pointTotals.sort(reverse=True, key=lambda s: int(s.split("_")[0]))

        # printdbg(f"Point toals after sorting high to low are: {pointTotals}", 3)

        # Actually pair the players utilizing graph theory networkx
        for points in pointTotals:
            # printdbg(points, 5)

            # Create the graph object and add all players to it
            bracketGraph = nx.Graph()
            bracketGraph.add_nodes_from(pointLists[points])

            # printdbg(pointLists[points], 5)
            # printdbg(bracketGraph.nodes(), 5)

            # Create edges between all players in the graph who haven't already played
            for player in bracketGraph.nodes():
                for opponent in bracketGraph.nodes():
                    if (
                        opponent not in self.playersDict[player]["opponents"]
                        and player != opponent
                    ):
                        # Weight edges randomly between 1 and 9 to ensure pairings are not always the same with the same list of players
                        wgt = random.randint(1, 9)
                        # If a player has more points, weigh them the highest so they get paired first
                        if self.playersDict[player]["points"] > int(
                            points.split("_")[0]
                        ) or self.playersDict[opponent]["points"] > int(
                            points.split("_")[0]
                        ):
                            wgt = 10
                        # Create edge
                        bracketGraph.add_edge(player, opponent, weight=wgt)

            # Generate pairings from the created graph
            pairings = dict(nx.max_weight_matching(bracketGraph))

            # printdbg(pairings, 3)

            # Actually pair the players based on the matching we found
            for p, value in pairings.items():
                if p in pointLists[points]:
                    self.pairPlayers(p, value)
                    pointLists[points].remove(p)
                    pointLists[points].remove(pairings[p])

            # printdbg(pointLists[points], 5)

            # Check if we have an odd man out that we need to pair down
            if len(pointLists[points]) > 0:
                # Check to make sure we aren't at the last player in the event
                # printdbg(f"Player {pointLists[points][0]} left in {points}. The index is {pointTotals.index(points)} and the length of totals is {len(pointTotals)}", 3)
                if pointTotals.index(points) + 1 == len(pointTotals):
                    while len(pointLists[points]) > 0:
                        # If they are the last player give them a bye
                        self.assignBye(pointLists[points].pop(0))
                else:
                    # Add our player to the next point group down
                    nextPoints = pointTotals[pointTotals.index(points) + 1]

                    while len(pointLists[points]) > 0:
                        pointLists[nextPoints].append(pointLists[points].pop(0))

        # Reassign players with fixed seating needs
        openTables = []
        displacedMatches = []

        # Create a copy of the pairings so we can edit the pairings during the loop
        clonePairings = self.roundPairings.copy()

        for table in clonePairings:
            p1 = self.roundPairings[table][0]
            p2 = self.roundPairings[table][1]

            # Check to see if either of our players needs fixed seating
            if self.playersDict[p1]["fixed_seating"]:
                fixed = self.playersDict[p1]["fixed_seating"]
            elif self.playersDict[p2]["fixed_seating"]:
                fixed = self.playersDict[p2]["fixed_seating"]
            else:
                fixed = False

            if fixed and fixed != table:
                if fixed in self.roundPairings:
                    # Check to see if the fixed table has been assigned to a match
                    displacedMatches.append(self.roundPairings.pop(fixed))

                # Note that the table that had been assigned is now open
                openTables.append(table)
                print(openTables)

                # Move the match
                # printdbg(f"[Fixed Seating] Moving table {table} to table {fixed}", 2)
                self.roundPairings[fixed] = self.roundPairings.pop(table)

        # Assign players displaced by a fixed seating to new tables
        for match in displacedMatches:
            if len(openTables):
                self.roundPairings[openTables[0]] = match
                del openTables[0]
            else:
                self.pairPlayers(match[0], match[1])

        # If there are open tables still, remove them from the matches out
        for table in openTables:
            self.tablesOut.remove(table)

        # Return the pairings for this round
        return self.roundPairings

    def pairPlayers(self, p1, p2):
        # printdbg(f"Pairing players {p1} and {p2}", 5)

        self.playersDict[p1]["opponents"].append(p2)
        self.playersDict[p2]["opponents"].append(p1)

        self.roundPairings[self.openTable] = [p1, p2]
        self.tablesOut.append(self.openTable)

        self.openTable += 1

    def assignBye(self, player):
        # printdbg(f"{player} got the bye", 2)
        self.playersDict[player]["results"].append([0, 0])

        self.playersDict[player]["opponents"].append("bye")

        # Add points for "winning"
        self.playersDict[player]["points"] += byePoints

    def reportMatch(self, table: int, result: list[int, int]):
        # table is an integer of the table number, result is a list of scores
        p1 = self.roundPairings[table][0]
        p2 = self.roundPairings[table][1]

        if result[0] == result[1]:
            # If values are the same they drew! Give'em each a point
            self.playersDict[p1]["points"] += drawPoints
            self.playersDict[p1]["results"].append(result)
            self.playersDict[p2]["points"] += drawPoints
            self.playersDict[p2]["results"].append(result)

        elif result[0] > result[1]:
            self.playersDict[p1]["points"] += winPoints
            # printdbg(f"Adding result {result} for player {p1}", 3)
            self.playersDict[p1]["results"].append(result)
            otresult = [result[1], result[0]]
            # printdbg(f"Adding result {otresult} for player {p2}", 3)
            self.playersDict[p2]["results"].append(otresult)

        elif result[1] > result[0]:
            self.playersDict[p2]["points"] += winPoints
            # printdbg(f"Adding result {result} for player {p1}", 3)
            self.playersDict[p1]["results"].append(result)
            otresult = [result[1], result[0]]
            # printdbg(f"Adding result {otresult} for player {p2}", 3)
            self.playersDict[p2]["results"].append(otresult)

        # Remove table reported from open tables
        self.tablesOut.remove(table)

        # When the last table reports, update tie breakers automatically
        if not len(self.tablesOut):
            self.calculateTieBreakers()

    def calculateTieBreakers(self):
        for p in self.playersDict:
            opponentWinPercents = []
            # Loop through all opponents
            for opponent in self.playersDict[p]["opponents"]:
                # Make sure it isn't a bye
                if opponent != "bye":
                    # Calculate win percent out to five decimal places, minimum of .33 per person
                    winPercent = max(
                        self.playersDict[opponent]["points"]
                        / float((len(self.playersDict[opponent]["opponents"]) * 3)),
                        0.33,
                    )
                    # printdbg(f"{opponent} contributed {winPercent} breakers", 3)
                    opponentWinPercents.append(winPercent)

            # Make sure we have opponents
            if len(opponentWinPercents):
                self.playersDict[p]["OMW%"] = "%.5f" % (
                    sum(opponentWinPercents) / float(len(opponentWinPercents))
                )


# def printdbg(msg, level=1):
#     if dbg == True and level <= debuglevel:
#         print(msg)
