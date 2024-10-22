import random
import argparse
import time
import threading

""" Game Play Instructions
For a two player human game: python IS211_Assignment8.py --player1 human --player2 human --timed
For a human against computer game: python IS211_Assignment8.py --player1 human --player2 computer --timed
"""

class Player:
    """Represents a player in the game of Pig."""

    def __init__(self, name):
        """Initializes a new Player object with the given name."""
        self.name = name
        self.score = 0
        self.turn_score = 0

    def hold(self):
        """Adds the current turn score to the player's total score and resets the turn score."""
        self.score += self.turn_score
        self.turn_score = 0

    def reset_turn_score(self):
        """Resets the player's turn score to 0."""
        self.turn_score = 0

class ComputerPlayer(Player):
    """Represents a computer player in the game of Pig."""
    
    def __init__(self, name):
        super().__init__(name)
    
    def take_turn(self, die):
        """Computer strategy: hold if turn score >= min(25, 100 - total score), else roll."""
        print(f"{self.name}'s turn (Computer). Current score: {self.turn_score}, Total score: {self.score}")
        while True:
            if self.turn_score >= min(25, 100 - self.score):
                print(f"{self.name} decides to hold.")
                self.hold()
                break
            else:
                roll = die.roll()
                print(f"{self.name} rolled a {roll}")
                if roll == 1:
                    print(f"{self.name} loses this turn's points!")
                    self.reset_turn_score()
                    break
                else:
                    self.turn_score += roll
                    print(f"{self.name} turn score: {self.turn_score}")

class Die:
    """Represents a six-sided die."""

    def __init__(self, sides=6):
        """Initializes a new Die object with the specified number of sides."""
        self.sides = sides

    def roll(self):
        """Rolls the die and returns a random number between 1 and the number of sides."""
        return random.randint(1, self.sides)

class Game:
    """Represents a game of Pig."""

    def __init__(self, player_names):
        """Initializes a new Game object with the specified player names."""
        self.die = Die()
        self.players = player_names
        self.current_player = 0  # Use index for current player

    def switch_turn(self):
        """Switches to the next player's turn."""
        self.current_player = (self.current_player + 1) % len(self.players)

    def play_turn(self):
        """Plays a single turn for the current player."""
        current_player = self.players[self.current_player]
        if isinstance(current_player, ComputerPlayer):
            current_player.take_turn(self.die)
        else:
            print(f"{current_player.name}'s turn. Current score: {current_player.turn_score}, Total score: {current_player.score}")
            while True:
                decision = input("Press 'r' to roll or 'h' to hold: ").strip().lower()
                if decision == 'r':
                    roll = self.die.roll()
                    print(f"{current_player.name} rolled a {roll}")
                    if roll == 1:
                        print(f"{current_player.name} loses this turn's points!")
                        current_player.reset_turn_score()
                        break
                    else:
                        current_player.turn_score += roll
                        self.display_scorecard()
                elif decision == 'h':
                    current_player.hold()
                    self.display_scorecard()
                    break
                else:
                    print("Invalid input. Please choose 'r' to roll or 'h' to hold.")

    def display_scorecard(self):
        """Displays the current scores for all players."""
        print("\nCurrent Scores:")
        for player in self.players:
            print(f"{player.name}: {player.score}")
        print()

    def check_winner(self):
        """Checks if a player has won the game."""
        for player in self.players:
            if player.score >= 100:
                return player
        return None

    def play_game(self):
        """Plays the entire game of Pig."""
        while True:
            self.play_turn()
            winner = self.check_winner()
            if winner:
                print(f"{winner.name} wins with a score of {winner.score}!")
                break
            self.switch_turn()

class PlayerFactory:
    """Factory to create players."""
    
    @staticmethod
    def create_player(player_type, name):
        """
        Factory method to create either a human or computer player.
        This method abstracts the player creation logic, making it easier to add new player types in the future.
        """
        if player_type == 'human':
            return Player(name)
        elif player_type == 'computer':
            return ComputerPlayer(name)
        else:
            raise ValueError("Invalid player type. Choose 'human' or 'computer'.")

class TimedGameProxy:
    """Proxy for the Game class to enforce a 1-minute time limit."""
    
    def __init__(self, game):
        """
        Initializes the proxy with the original game instance.
        Starts the timer thread to track the game duration.
        """
        self.game = game
        self.start_time = time.time()
        self.time_limit = 60  # 1 minute
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()
    
    def run_timer(self):
        """Runs a timer and displays time remaining."""
        while True:
            elapsed_time = time.time() - self.start_time
            remaining_time = self.time_limit - elapsed_time
            if remaining_time <= 0:
                print("\nTime's up!")
                self.declare_winner()
                break
            time.sleep(1)

    def play_turn(self):
        """Check if the game is within time limit before playing a turn."""
        if time.time() - self.start_time > self.time_limit:
            print("\nTime's up!")
            self.declare_winner()
        else:
            print(f"Time remaining: {int(self.time_limit - (time.time() - self.start_time))} seconds")
            self.game.play_turn()

    def declare_winner(self):
        """Declare the player with the highest score as the winner."""
        winner = max(self.game.players, key=lambda player: player.score)
        print(f"{winner.name} wins with a score of {winner.score}!")
        exit()  # End the game
    
    def play_game(self):
        """Play the game with the time limit."""
        while True:
            print()  # Print a newline for clarity
            self.play_turn()
            winner = self.game.check_winner()
            if winner:
                print(f"{winner.name} wins with a score of {winner.score}!")
                break
            self.game.switch_turn()

def add_player_names(num_players):
    """Prompts for player names based on the specified number of players."""
    players = []
    for i in range(num_players):
        name = input(f"Enter the name for Player {i + 1}: ")
        players.append(name)
    return players

def main():
    """Main function to start the game."""
    parser = argparse.ArgumentParser(description="Play a game of Pig!")
    parser.add_argument('--player1', type=str, default='human', help="Type of Player 1 (human/computer)")
    parser.add_argument('--player2', type=str, default='human', help="Type of Player 2 (human/computer)")
    parser.add_argument('--timed', action='store_true', help="Play a timed version of the game (1 minute limit)")
    args = parser.parse_args()

    # Create players using the factory
    player_names = []
    player_types = [args.player1, args.player2]

    for player_type in player_types:
        if player_type == 'human':
            name = input(f"Enter the name for {player_type.capitalize()} Player: ")
            player_names.append(Player(name))
        elif player_type == 'computer':
            name = f"Computer Player {len(player_names) + 1}"
            player_names.append(ComputerPlayer(name))

    # Start the game
    game = Game(player_names)
    
    # If timed option is set, use the TimedGameProxy
    if args.timed:
        proxy_game = TimedGameProxy(game)
        proxy_game.play_game()
    else:
        game.play_game()

if __name__ == "__main__":
    main()