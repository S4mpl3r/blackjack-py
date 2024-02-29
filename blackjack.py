import json
import re
from random import shuffle
from time import sleep
from typing import List, Tuple

from rich import box
from rich.align import Align
from rich.console import Console
from rich.table import Table

SAVE_PATH = "./save.json"

console = Console()


class BlackJack:
    def __init__(self, num_of_decks=1) -> None:
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = [
            "Ace",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
        ]
        self.values = {
            "Ace": 11,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "Jack": 10,
            "Queen": 10,
            "King": 10,
        }
        self.num_of_decks = num_of_decks
        self.is_blackjack = False
        self.shuffle = False
        self.create_deck()

    def create_deck(self) -> None:
        new_deck = [(rank, suit) for suit in self.suits for rank in self.ranks]
        # Shuffle the deck
        shuffle(new_deck)
        self.deck = new_deck
        self.discarded = []

    def deal_cards(self) -> List[Tuple[str, str]]:
        if len(self.deck) < 4:
            show_spinner(
                duration=3, title="The deck is running low, shuffling a new deck..."
            )
            self.create_deck()

        player_hand = [self.deck.pop(), self.deck.pop()]
        dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.discarded.extend(player_hand + dealer_hand)
        if (
            self.calculate_hand(player_hand) == 21
            or self.calculate_hand(dealer_hand) == 21
        ):
            self.is_blackjack = True
        return player_hand, dealer_hand

    def calculate_hand(self, hand: List[Tuple[str, str]]) -> int:
        total = sum(self.values[card[0]] for card in hand)
        # Account for aces
        num_aces = sum(card[0] == "Ace" for card in hand)
        while total > 21 and num_aces:
            total -= 10
            num_aces -= 1
        return total

    def player_turn(self, player_hand: List[Tuple[str, str]]) -> str:
        if len(player_hand) > 2:
            console.print("[yellow]Player cards: ")
        # print_hand(player_hand, "Player", self, spin=False)
        while True:
            index = len(player_hand)
            if index > 2:
                print_hand(player_hand[: index - 1], self, spin=False)
                print_hand(player_hand[index - 1 :], self)
                print_total(self, player_hand)

            action = console.input("Do you want to hit or stand? ").lower()
            if action in ["hit", "h"]:
                if len(self.deck) < 1:
                    self.deck.extend(self.discarded)
                    self.shuffle = True

                player_hand.append(self.deck.pop())
                self.discarded.append(player_hand[-1])
                score = self.calculate_hand(player_hand)
                if score > 21:
                    print_hand(player_hand[:index], self, spin=False)
                    print_hand(player_hand[index:], self)
                    print_total(self, player_hand)
                    console.print("[red]Bust! You lose.")
                    return "dealer"
                elif score == 21:
                    print_hand(player_hand[:index], self, spin=False)
                    print_hand(player_hand[index:], self)
                    print_total(self, player_hand)
                    return "player"
            else:
                return "player"

    def dealer_turn(self, dealer_hand: List[Tuple[str, str]]) -> str:
        console.print("[blue]Dealer cards: ")
        print_hand(dealer_hand[:1], self, spin=False)
        print_hand(dealer_hand[1:], self)
        while self.calculate_hand(dealer_hand) < 17:
            index = len(dealer_hand)
            if len(self.deck) < 1:
                self.deck.extend(self.discarded)
                self.shuffle = True

            dealer_hand.append(self.deck.pop())
            self.discarded.append(dealer_hand[-1])
            print_hand(dealer_hand[index:], self)

        print_total(self, dealer_hand)

    def determine_winner(
        self, player_hand: List[Tuple[str, str]], dealer_hand: List[Tuple[str, str]]
    ) -> str:
        player_total = self.calculate_hand(player_hand)
        dealer_total = self.calculate_hand(dealer_hand)
        if player_total > 21:
            return "dealer"
        elif dealer_total > 21:
            return "player"
        elif player_total > dealer_total:
            return "player"
        elif dealer_total > player_total:
            return "dealer"
        else:
            return "push"


def show_spinner(duration=1, title="", spinner="dots") -> None:
    with console.status(
        title, spinner=spinner, spinner_style="white", speed=3
    ) as status:
        sleep(duration)


def print_hand(hand: List[Tuple[str, str]], blackjack: BlackJack, spin=True) -> None:
    for card in hand:
        if spin:
            show_spinner()
        if card != "?":
            suit = ":" + card[1].lower() + ":"
            color = "red" if card[1] in ["Hearts", "Diamonds"] else "black"
            number = "blank"
            if card[0] == "Ace":
                number = "A"
            else:
                number = str(blackjack.values[card[0]])
            console.print(f"[{color} bold]{suit}{number}")
        else:
            console.print(f"?")


def print_total(blackjack: BlackJack, hand: List[Tuple[str, str]]) -> None:
    console.print(f"[white]({blackjack.calculate_hand(hand)} total)")


def play_game(balance: float) -> None:
    blackjack = BlackJack()

    console.clear()
    show_spinner(duration=1.5, title="[blue]Shuffling...")
    # Play the game
    while True:
        bet = collect_bet(balance)
        balance -= bet
        console.clear()
        console.print(f"[yellow]Chips owned: ${balance} | Bet amount: ${bet}")

        player_hand, dealer_hand = blackjack.deal_cards()
        console.print("Dealer cards: ")
        print_hand([dealer_hand[0], "?"], blackjack)
        console.print("Player cards: ")
        print_hand(player_hand, blackjack)
        print_total(blackjack, player_hand)
        if not blackjack.is_blackjack:
            # Player turn
            player_result = blackjack.player_turn(player_hand)
            # Dealer turn
            if player_result == "player":
                blackjack.dealer_turn(dealer_hand)
        # Determine the winner
        winner = blackjack.determine_winner(player_hand, dealer_hand)
        if winner == "player":
            console.print("[green]You win!")
            if blackjack.is_blackjack:
                console.print("[green]Blackjack!:joker:")
                balance += bet * 2.5
                console.print(f"[yellow]Your balance: ${balance}")
            else:
                balance += bet * 2
                console.print(f"[yellow]Your balance: ${balance}")
        elif winner == "dealer":
            console.print("[red]Dealer wins!")
            if blackjack.is_blackjack:
                console.print("[red]Dealer has a blackjack :(")
        else:
            console.print("Push!")
            balance += bet
        if blackjack.shuffle:
            show_spinner(duration=3, title="Shuffling new deck...")
            blackjack.create_deck()
            blackjack.shuffle = False
        blackjack.is_blackjack = False
        # Ask the player if they want to play again
        if balance > 0:
            play_again = console.input("Do you want to play again? (y/n) ").lower()
            if play_again != "y":
                return balance
        else:
            console.input("[red]Out of money! Press any key to continue.")
            return 0


def print_main_menu(balance: float) -> None:
    console.clear()
    table = Table(border_style="yellow", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Welcome to [yellow italic]BLACKJACK[/]:joker:", justify="left")

    color = "green"
    if balance <= 0:
        color = "red"
    table.add_row(f"Chips owned: [{color}]${balance}")
    table.add_row("1. Play")
    table.add_row("2. Get chips")
    table.add_row("3. Save/Load")
    table.add_row("4. Exit")
    table_centered = Align.left(table)

    console.print(table_centered)


def deposit_money() -> float:
    money = 0
    while True:
        console.clear()
        money = console.input("Enter the amount: ").strip()
        if is_float(money):
            money = float(money)
            show_spinner(duration=1.5, title="[green]Getting chips...", spinner="arrow")
            break
        else:
            console.input("[red]Please enter a valid number.")
    return money


def collect_bet(balance: float) -> float:
    while True:
        console.clear()
        console.print(f"Chips owned: $[green]{balance}")
        bet = console.input(
            f"Enter a bet amount: (minimum = $1, maximum = ${balance}) "
        ).strip()
        if is_float(bet):
            bet = float(bet)
            if bet <= balance and bet > 0:
                return bet
            else:
                console.input("[red] Invalid amount. Please try again")
        else:
            console.input("[red] Invalid amount. Please try again")


def save_load(balance: float) -> float:
    console.clear()
    console.print("Choose an option:\n1) Save")
    console.print("2) Load\n")
    key = console.input("[white](1/2): ").strip()
    if key not in [*"12"]:
        console.input("[red]Failed. Try again")
    else:
        if key == "1":
            console.clear()
            show_spinner(duration=1.5, title="[blue]Saving...", spinner="dots10")
            with open(SAVE_PATH, "w") as f:
                json.dump({"balance": balance}, f)
                console.input("[green]Save successful. Press any key to continue ")
            return balance
        elif key == "2":
            console.clear()
            show_spinner(duration=1.5, title="[blue]Loading...", spinner="dots10")
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
                console.input("[green]Load successful. Press any key to continue ")

            return data["balance"]


def is_float(str: str) -> bool:
    pattern = r"^[+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
    return bool(re.match(pattern, str))


def main() -> None:
    balance = 0
    while True:
        print_main_menu(balance)
        key = console.input("[white]Choose an option (1-4): ")
        if key not in [*"1234"]:
            console.input("[red]Not a valid option. Try again")
        if key == "1":
            if balance > 0:
                balance = play_game(balance)
            else:
                console.input("[red] No money! Please deposit money first.")
        elif key == "2":
            balance += deposit_money()
        elif key == "3":
            balance = save_load(balance)
        elif key == "4":
            break


if __name__ == "__main__":
    main()
