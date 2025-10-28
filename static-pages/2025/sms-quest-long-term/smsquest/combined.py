from pyscript import window

import re
import sys
import inspect
try:
    import readline  # noqa: adds readline semantics to input()
except ImportError:
    pass
import textwrap
import random
from copy import deepcopy
try:
    from shutil import get_terminal_size
except ImportError:
    try:
        from backports.shutil_get_terminal_size import get_terminal_size
    except ImportError:
        def get_terminal_size(fallback=(80, 24)):
            return fallback

__version__ = '1.2.1'
__all__ = (
    'when',
    'start',
    'AdvRoom',
    'AdvItem',
    'Bag',
    'say',
    'set_context',
    'get_context',
)


# --- App Classes ---

from typing import Optional, Callable
from enum import Enum


# --- Main App ---
import os, time
from enum import Enum
import json



#: The current context.
#:
#: Commands will only be available if their context is "within" the currently
#: active context, a functiondefined by '_match_context()`.
current_context = None


#: The separator that defines the context hierarchy
CONTEXT_SEP = '.'


def set_context(new_context):
    """Set current context.

    Set the context to `None` to clear the context.

    """
    global current_context
    _validate_context(new_context)
    current_context = new_context


def get_context():
    """Get the current command context."""
    return current_context


def _validate_context(context):
    """Raise an exception if the given context is invalid."""
    if context is None:
        return

    err = []
    if not context:
        err.append('be empty')
    if context.startswith(CONTEXT_SEP):
        err.append('start with {sep}')
    if context.endswith(CONTEXT_SEP):
        err.append('end with {sep}')
    if CONTEXT_SEP * 2 in context:
        err.append('contain {sep}{sep}')
    if err:
        if len(err) > 1:
            msg = ' or '.join([', '.join(err[:-1]), err[-1]])
        else:
            msg = err[0]
        msg = 'Context {ctx!r} may not ' + msg
        raise ValueError(msg.format(sep=CONTEXT_SEP, ctx=context))


def _match_context(context, active_context):
    """Return True if `context` is within `active_context`.

    adventurelib offers a hierarchical system of contexts defined with a
    dotted-string notation.

    A context matches if the active context is "within" the pattern's context.

    For example:

    * ``ham.spam`` is within ``ham.spam``
    * ``ham.spam`` is within ``ham``
    * ``ham.spam`` is within ``None``.
    * ``ham.spam`` is not within ``ham.spam.eggs``
    * ``ham.spam`` is not within ``spam`` or ``eggs``
    * ``None`` is within ``None`` and nothing else.

    """
    if context is None:
        # If command has no context, it always matches
        return True

    if active_context is None:
        # If the command has a context, and we don't, no match
        return False

    # The active_context matches if it starts with context and is followed by
    # the end of the string or the separator
    clen = len(context)
    return (
        active_context.startswith(context) and
        active_context[clen:clen + len(CONTEXT_SEP)] in ('', CONTEXT_SEP)
    )


class InvalidCommand(Exception):
    """A command is not defined correctly."""


class InvalidDirection(Exception):
    """The direction specified was not pre-declared."""


class Placeholder:
    """Match a word in a command string."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.upper()


class AdvRoom:
    """A generic room object that can be used by game code."""

    _directions = {}

    @staticmethod
    def add_direction(forward, reverse):
        """Add a direction."""
        for dir in (forward, reverse):
            if not dir.islower():
                raise InvalidCommand(
                    'Invalid direction %r: directions must be all lowercase.'
                )
            if dir in AdvRoom._directions:
                raise KeyError('%r is already a direction!' % dir)
        AdvRoom._directions[forward] = reverse
        AdvRoom._directions[reverse] = forward

        # Set class attributes to None to act as defaults
        setattr(AdvRoom, forward, None)
        setattr(AdvRoom, reverse, None)

    def __init__(self, description):
        self.description = description.strip()

        # Copy class Bags to instance variables
        for k, v in vars(type(self)).items():
            if isinstance(v, Bag):
                setattr(self, k, deepcopy(v))

    def __str__(self):
        return self.description

    def exit(self, direction):
        """Get the exit of a room in a given direction.

        Return None if the room has no exit in a direction.

        """
        if direction not in self._directions:
            raise KeyError('%r is not a direction' % direction)
        return getattr(self, direction, None)

    def exits(self):
        """Get a list of directions to exit the room."""
        return sorted(d for d in self._directions if getattr(self, d))

    def __setattr__(self, name, value):
        if isinstance(value, AdvRoom):
            if name not in self._directions:
                raise InvalidDirection(
                    '%r is not a direction you have declared.\n\n' +
                    'Try calling Room.add_direction(%r, <opposite>) ' % name +
                    ' where <opposite> is the return direction.'
                )
            reverse = self._directions[name]
            object.__setattr__(self, name, value)
            object.__setattr__(value, reverse, self)
        else:
            object.__setattr__(self, name, value)


AdvRoom.add_direction('north', 'south')
AdvRoom.add_direction('east', 'west')


class AdvItem:
    """A generic item object that can be referred to by a number of names."""

    def __init__(self, name, *aliases):
        self.name = name
        self.aliases = tuple(
            label.lower()
            for label in (name,) + aliases
        )

    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join(repr(n) for n in self.aliases)
        )

    def __str__(self):
        return self.name


class Bag(set):
    """A collection of Items, such as in an inventory.

    Behaves very much like a set, but the 'in' operation is overloaded to
    accept a str item name, and there is a ``take()`` method to remove an item
    by name.

    """
    def find(self, name):
        """Find an object in the bag by name, but do not remove it.

        Return None if the name does not match.

        """
        for item in self:
            if name.lower() in item.aliases:
                return item
        return None

    def __contains__(self, v):
        """Return True if an Item is present in the bag.

        If v is a str, then find the item by name, otherwise find the item by
        identity.

        """
        if isinstance(v, str):
            return bool(self.find(v))
        else:
            return set.__contains__(v)

    def take(self, name):
        """Remove an Item from the bag if it is present.

        If multiple names match, then return one of them.

        Return None if no item matches the name.

        """
        obj = self.find(name)
        if obj is not None:
            self.remove(obj)
        return obj

    def get_random(self):
        """Choose an Item from the bag at random, but don't remove it.

        Return None if the bag is empty.

        """
        if not self:
            return None
        which = random.randrange(len(self))
        for index, obj in enumerate(self):
            if index == which:
                return obj

    def take_random(self):
        """Remove an Item from the bag at random, and return it.

        Return None if the bag is empty.

        """
        obj = self.get_random()
        if obj is not None:
            self.remove(obj)
        return obj


def _register(command, func, context=None, kwargs={}):
    """Register func as a handler for the given command."""
    pattern = Pattern(command, context)
    sig = inspect.signature(func)
    func_argnames = set(sig.parameters)
    when_argnames = set(pattern.argnames) | set(kwargs.keys())
    if func_argnames != when_argnames:
        raise InvalidCommand(
            'The function %s%s has the wrong signature for @when(%r)' % (
                func.__name__, sig, command
            ) + '\n\nThe function arguments should be (%s)' % (
                ', '.join(pattern.argnames + list(kwargs.keys()))
            )
        )

    commands.append((pattern, func, kwargs))


class Pattern:
    """A pattern for matching a command.

    Patterns are defined with a string like 'take ITEM' which corresponds to
    matching 'take' exactly followed by capturing one or more words as the
    group named 'item'.
    """

    def __init__(self, pattern, context=None):
        self.orig_pattern = pattern
        _validate_context(context)
        self.pattern_context = context
        words = pattern.split()
        match = []
        argnames = []
        self.placeholders = 0
        for w in words:
            if not w.isalpha():
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    'Commands may consist of letters only.'
                )
            if w.isupper():
                arg = w.lower()
                if arg in argnames:
                    raise InvalidCommand(
                            'Invalid command %r' % pattern +
                            ' Identifiers may only be used once'
                            )
                argnames.append(arg)
                match.append(Placeholder(arg))
                self.placeholders += 1
            elif w.islower():
                match.append(w)
            else:
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    '\n\nWords in commands must either be in lowercase or ' +
                    'capitals, not a mix.'
                )
        self.argnames = argnames
        self.prefix = []
        for w in match:
            if isinstance(w, Placeholder):
                break
            self.prefix.append(w)
        self.pattern = match[len(self.prefix):]
        self.fixed = len(self.pattern) - self.placeholders

    def __repr__(self):
        ctx = ''
        if self.pattern_context:
            ctx = ', context=%r' % self.pattern_context
        return '%s(%r%s)' % (
            type(self).__name__,
            self.orig_pattern,
            ctx
        )

    @staticmethod
    def word_combinations(have, placeholders):
        """Iterate over possible assignments of words in have to placeholders.

        `have` is the number of words to allocate and `placeholders` is the
        number of placeholders that those could be distributed to.

        Return an iterable of tuples of integers; the length of each tuple
        will match `placeholders`.

        """
        if have < placeholders:
            return
        if have == placeholders:
            yield (1,) * placeholders
            return
        if placeholders == 1:
            yield (have,)
            return

        # Greedy - start by taking everything
        other_groups = placeholders - 1
        take = have - other_groups
        while take > 0:
            remain = have - take
            if have >= placeholders - 1:
                combos = Pattern.word_combinations(remain, other_groups)
                for buckets in combos:
                    yield (take,) + tuple(buckets)
            take -= 1  # backtrack

    def is_active(self):
        """Return True if a command is active in the current context."""
        return _match_context(self.pattern_context, current_context)

    def ctx_order(self):
        """Return an integer indicating how nested the context is."""
        if not self.pattern_context:
            return 0
        return self.pattern_context.count(CONTEXT_SEP) + 1

    def match(self, input_words):
        """Match a given list of input words against this pattern.

        Return a dict of captured groups if the pattern matches, or None if
        the pattern does not match.

        """
        global current_context

        if len(input_words) < len(self.argnames):
            return None

        if input_words[:len(self.prefix)] != self.prefix:
            return None

        input_words = input_words[len(self.prefix):]

        if not input_words and not self.pattern:
            return {}
        if bool(input_words) != bool(self.pattern):
            return None

        have = len(input_words) - self.fixed

        for combo in self.word_combinations(have, self.placeholders):
            matches = {}
            take = iter(combo)
            inp = iter(input_words)
            try:
                for cword in self.pattern:
                    if isinstance(cword, Placeholder):
                        count = next(take)
                        ws = []
                        for _ in range(count):
                            ws.append(next(inp))
                        matches[cword.name] = ws
                    else:
                        word = next(inp)
                        if cword != word:
                            break
                else:
                    return {k: ' '.join(v) for k, v in matches.items()}
            except StopIteration:
                continue
        return None


def prompt():
    """Called to get the prompt text."""
    return '> '


def no_command_matches(command):
    """Called when a command is not understood."""
    print("I don't understand '%s'." % command)


def when(command, context=None, **kwargs):
    """Decorator for command functions."""
    def dec(func):
        _register(command, func, context, kwargs)
        return func
    return dec


def help():
    """Print a list of the commands you can give."""
    print('Here is a list of the commands you can give:')
    cmds = sorted(c.orig_pattern for c, _, _ in commands if c.is_active())
    for c in cmds:
        print(c)


def _available_commands():
    """Return the list of available commands in the current context.

    The order will be the order in which they should be considered, which
    corresponds to how deeply nested the context is.

    """
    available_commands = []
    for c in commands:
        pattern = c[0]
        if pattern.is_active():
            available_commands.append(c)
    available_commands.sort(
        key=lambda c: c[0].ctx_order(),
        reverse=True,
    )
    return available_commands


def _handle_command(cmd):
    """Handle a command typed by the user."""
    ws = cmd.lower().split()

    for pattern, func, kwargs in _available_commands():
        args = kwargs.copy()
        matches = pattern.match(ws)
        if matches is not None:
            args.update(matches)
            func(**args)
            break
    else:
        no_command_matches(cmd)
    print()


def start(help=True):
    """Run the game."""
    if help:
        # Ugly, but we want to keep the arguments consistent
        help = globals()['help']
        qmark = Pattern('help')
        qmark.prefix = ['?']
        qmark.orig_pattern = '?'
        commands.insert(0, (Pattern('help'), help, {}))
        commands.insert(0, (qmark, help, {}))
    while True:
        try:
            cmd = input(prompt()).strip()
        except EOFError:
            print()
            break

        if not cmd:
            continue

        _handle_command(cmd)


def say(msg):
    """Print a message.

    Unlike print(), this deals with de-denting and wrapping of text to fit
    within the width of the terminal.

    Paragraphs separated by blank lines in the input will be wrapped
    separately.

    """
    msg = str(msg)
    msg = re.sub(r'^[ \t]*(.*?)[ \t]*$', r'\1', msg, flags=re.M)
    width = get_terminal_size()[0]
    paragraphs = re.split(r'\n(?:[ \t]*\n)', msg)
    formatted = (textwrap.fill(p.strip(), width=width) for p in paragraphs)
    print('\n\n'.join(formatted))


commands = [
    (Pattern('quit'), sys.exit, {}),  # quit command is built-in
]


# --- Dispatch ---

# Custom dispatch function since adventurelib doesn't expose one
def dispatch_command(cmd):
    """Handle a command and return the result instead of printing it."""
    ws = cmd.lower().split()
    
    # Get available commands from adventurelib's internal function
    available_commands = []
    for c in commands:
        pattern = c[0]
        if pattern.is_active():
            available_commands.append(c)
    available_commands.sort(
        key=lambda c: c[0].ctx_order(),
        reverse=True,
    )
    
    # Try to match the command
    for pattern, func, kwargs in available_commands:
        args = kwargs.copy()
        matches = pattern.match(ws)
        if matches is not None:
            args.update(matches)
            # Call the function and capture its return value
            try:
                result = func(**args)
                return result if result is not None else "OK"
            except Exception as e:
                return f"Error: {str(e)}"
    
    # No command matched
    return None


'''
app_classes.py
'''
class Context(str, Enum):
    EXPLORING = "exploring"
    USING_PHONE = "using_phone"
    USING_SAFE = "using_safe"


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Item(AdvItem):
    def __init__(
        self,
        name: str,
        *aliases: str,
        def_name: str = "",
        indef_name: str = "",
        description: str = ""
    ):
        super().__init__(name, *aliases)
        self.def_name = def_name
        self.indef_name = indef_name
        self.description = description


class LockedExit:
    def __init__(self, description: str, unlock_item: Optional[Item] = None):
        self.is_locked: bool = True
        self.description: str = description
        self.unlock_item: Optional[Item] = unlock_item


class Room(AdvRoom):
    def __init__(
        self,
        static_description: Optional[str] = "",
        illegal_direction_description: Optional[dict[Direction, str]] = None,
        functional_description: Optional[Callable[['Room'], str]] = None,
        first_time_description: Optional[str] = None,
        items: Optional[list[Item]] = None,
        fixtures: Optional[list[Item]] = None,
        locked_exits: Optional[dict[str, LockedExit]] = None,
        is_dark: Optional[bool] = False,
        dark_safe_exit: Optional[Direction] = None,
        dark_description: Optional[str] = "The room is dark.",
        room_aliases: Optional[list[str]] = None
    ):
        super().__init__(static_description)

        if not static_description and not functional_description:
            raise ValueError("You must provide either static_description or functional_description for Rooms.")

        self.first_time_in_room = True
        self.first_time_description = first_time_description
        self.items = Bag(items) if items is not None else Bag()
        self.fixtures = Bag(fixtures) if fixtures is not None else Bag()
        self.locked_exits = locked_exits if locked_exits is not None else {}
        self.is_dark = is_dark
        self.dark_safe_exit = dark_safe_exit
        self.dark_description = dark_description
        self.functional_description = functional_description
        self.illegal_direction_description = illegal_direction_description
        self.room_aliases = room_aliases if room_aliases is not None else []

    def get_description(self):
        if self.is_dark:
            return self.dark_description
        
        if self.first_time_in_room:
            self.first_time_in_room = False

            if self.first_time_description:
                return self.first_time_description
        
        if self.functional_description:
            return self.functional_description(self)
        else:
            return self.description


'''
game_state.py
'''
class GameState:
    CAT_HIDDEN = True
    CAT_OBTAINED = False
    CAN_FIND_WARDROBE_SECRET = False
    DISCOVERED_SEAGULLS = False
    
    # State specific to long-term mode
    OFFICE_COMPUTER = False
    OFFICE_POSTER = False
    OFFICE_STICKIES = False
    OFFICE_PAINTINGS = False
    OFFICE_TICKET = False

game_state = GameState()


"""
items.py
"""
empty_can = Item(
    'empty tin can', 'empty can', 'empty tin', 'can', 'tin', 'tin can',
    def_name='the empty tin can',
    indef_name='an empty tin can',
    description="An empty tin can, slightly dented and rusted.")

key = Item(
    'key', 'brass key', 'small key', 'small brass key',
    def_name='the key',
    indef_name='a key',
    description="A small brass key."
)

closed_can = Item(
    'sealed tin can', 'sealed can', 'sealed tin', 'closed tin can', 'closed can', 'closed tin', 'unopened tin can', 'unopened can', 'unopened tin', 'can', 'tin', 'tin can', 'food can', 'can of food', 'food',
    def_name='the sealed tin can',
    indef_name='a sealed tin can',
    description="A sealed tin can. It looks shiny and unused. There is a tab on the top that looks like it can be pulled to open it."
)

open_can = Item(
    'open tin can', 'opened tin can', 'open tin', 'opened tin', 'opened can', 'open can', 'can', 'tin', 'tin can', 'food can', 'can of food', 'food',
    def_name='the tin can',
    description="An open tin can. It has a brown mushy substance inside."
)

cat = Item(
    'cat',
    def_name='the cat',
    description="A fluffy gray cat. It looks up at you with big green eyes."
)

crowbar = Item(
    'crowbar',
    def_name='the crowbar',
    description="A worn, red crowbar, perfect for prying things open or beating up aliens."
)

stuffie = Item(
    'stuffie', "plushie", 'cute stuffie', "cute plushie",
    def_name='the stuffie',
    description="A cute, fluffy stuffed animal. It looks like some kind of purple cat with a hat..."
)

dry_rations = Item(
    'dry rations', 'rations',
    def_name='the dry rations',
    description="A pack of dry rations. It looks pretty old."
)

batteries = Item(
    'batteries', 'battery',
    def_name='the batteries',
    description="A pack of small, cylindrical batteries. They look like they still have some charge left."
)

flashlight_dead = Item(
    'flashlight',
    def_name='the flashlight',
    description="A flashlight that has run out of batteries. It looks like it could be useful if only it had some power."
)

flashlight_powered = Item(
    'flashlight',
    def_name='the flashlight',
    description="A flashlight that has power. You could probably use it to look into shadows."
)

fridge = Item(
    'fridge',
    def_name='the fridge',
    description="An old but functional refrigerator. It hums quietly. Opening it reveals a fresh sandwich on the shelf, its ingredients visible through clear plastic wrap."
)

fridge_no_sand = Item(
    'fridge',
    def_name='the fridge',
    description="An old but functional refrigerator. It hums quietly. Opening it reveals a barren shelf."
)

sandwich = Item(
    'sandwich',
    def_name='the sandwich',
    description="A sandwich wrapped in clear plastic. The sandwich is stuffed with turkey, crisp lettuce, ripe tomato slices, and cheese. Your stomach rumbles just looking at it."
)

wardrobe = Item(
    'wardrobe', 'cabinet',
    def_name='the wardrobe',
    description="An old wooden wardrobe. Looking inside you see a few shirts and a pair of pants."
)

wardrobe_investigated = Item(
    'wardrobe', 'cabinet',
    def_name='the wardrobe',
    description="An old wooden wardrobe. Looking inside you see a few shirts and a pair of pants."
)

wardrobe_with_secret = Item(
    'wardrobe', 'cabinet',
    def_name='the wardrobe',
    description="An old wooden wardrobe. Looking inside you see a few shirts and a pair of pants... Looking closer, it looks like there is a seam at the back of the wardrobe! You push on the back wall and it swings back, opening into darkness..."
)

wardrobe_with_secret_investigated = Item(
    'wardrobe', 'cabinet',
    def_name='the wardrobe',
    description="An old wooden wardrobe. Looking inside you see a few shirts and a pair of pants... Looking closer, it looks like there is a seam at the back of the wardrobe! You don't know how you could have missed this before? You push on the back wall and it swings back, opening into darkness..."
)

wardrobe_found_secret = Item(
    'wardrobe', 'cabinet',
    def_name='the wardrobe',
    description="An old wooden wardrobe. Looking inside you see a few shirts and a pair of pants, and an opening into darkness..."
)

bed = Item(
    'bed',
    def_name='the bed',
    description="A comfortable-looking bed with a fluffy comforter."
)

bedside = Item(
    'bedside', 'table', 'bedside table',
    def_name='the bedside table',
    description="A small bedside table with a lamp on it."
)

supplies = Item(
    'supplies',
    def_name='the supplies',
    description="Various supplies are stored on shelving along the walls, or stacked in haphazard piles."
)

breaker_closed = Item(
    'metal panel', 'panel', 'metal panel door', 'metal panel', 'metal door', 'door',
    def_name='the metal panel',
    description="The metal panel appears to be closed tightly. Maybe you could pry it open?"
)

breaker_open = Item(
    'metal panel', 'panel', 'metal panel door', 'metal panel', 'metal door', 'door', 'breaker',
    def_name='the metal panel',
    description="The opened metal panel reveals a circuit breaker. It looks like all of the circuit breakers are in the 'on' position except for one."
)

breaker_open_and_on = Item(
    'metal panel', 'panel', 'metal panel door', 'metal panel', 'metal door', 'door', 'breaker',
    def_name='the metal panel',
    description="The opened metal panel reveals a circuit breaker. It looks like all of the circuit breakers are in the 'on' position."
)


crates = Item(
    'crates', 'crate', 'box', 'boxes', 'wooden crates', 'wooden boxes',
    def_name='the wooden crates',
    description="Stacks and stacks of wooden crates. They look like they haven't been moved in a long time. There are odd markings on some of the crates, but you can't make any of them out in the light..."
)

open_crates = Item(
    'crates', 'crate', 'box', 'boxes', 'wooden crates', 'wooden boxes',
    def_name='the wooden crates',
    description="Stacks and stacks of wooden crates. They look like they haven't been moved in a long time. There are odd markings on some of the crates, but you can't make any of them out in the light..."
)

unobtainable_brass_key = Item(
    'brass key', 'key',
    def_name='the brass key',
    description="A small brass key."
)

table = Item(
    'table',
    def_name='the table',
    description="A sturdy wooden table. In the center is a small brass key."
)

vent = Item(
    'vent', 'mouse', 'mouse with key',
    def_name='the vent',
    description="The vent appears to have a medium-sized shafe, with a few bars in front. You can see a mouse with a key inside. You don't think you'd be able to fit into it even without the vent cover. Maybe you should rethink things next time you're considering an extra cookie..."
)

vent_empty = Item(
    'vent',
    def_name='the vent',
    description="The vent appears to have a medium-sized shafe, with a few bars in front. You don't think you'd be able to fit into it even without the vent cover. Thankfully the cat isn't as ... large ... as you are."
)

window_outside = Item(
    'window',
    def_name='the window',
    description="A small window. The inside is dimly lit, but it looks like there is a wooden workbench with some things on it."
)

window_inside = Item(
    'window',
    def_name='the window',
    description="A small window. You can see the beach outside."
)

phone = Item(
    'phone',
    def_name='the phone',
    description="A really old-looking phone. It looks like it could be used to make calls."
)

maps = Item(
    'maps',
    def_name='the maps',
    description="Several old maps are pinned to the walls. They seem to depict the local area and some nearby islands, but you're not familiar with the area."
)

nautical_memorabilia = Item(
    'memorabilia', 'nautical memorabilia',
    def_name='the nautical memorabilia',
    description="There is a large collection of sea-themed items attached to the walls, like a fishing net and an anchor. They seem pretty well attached to the walls."
)

workbench = Item(
    'workbench',
    def_name='the workbench',
    description="A sturdy wooden workbench. It's cluttered with papers and a phone."
)

papers = Item(
    'papers',
    def_name='the papers',
    description="You look through the papers. It looks like a madman's ramblings, with things scribbled all over. One says \"Do they see it all?\" and another says \"Call for answers\"... You can't make heads or tails of it..."
)

seagulls = Item(
    'seagulls',
    def_name='the seagulls',
    description="Several small seagulls are perched on the sand nearby."
)

metal_table_1 = Item(
    'table', 'metal table',
    def_name='the table',
    description="A small metal table. There is a notebook on it."
)

metal_table_2 = Item(
    'table', 'metal table',
    def_name='the table',
    description="A small metal table. There is nothing on it"
)

cushioned_chair = Item(
    'chair', 'cushioned chair',
    def_name='the cushioned chair',
    description="A cushioned chair. It looks a bit faded, but it looks like it would be pretty comfortable."
)

cot = Item(
    'cot',
    def_name='the cot',
    description="A cot. It has blankets and a pillow. It doesn't look particularly comfortable..."
)

notebook = Item(
    'notebook',
    def_name='the notebook',
    description="A notebook with a cloverleaf on the cover. It contains many pages of cryptic writing. One page has a to-do list on it with a few items. One is a note to not forget to put the rug back before leaving. Another is a reminder to buy more crackers. Another is a reminder to call home. There's also on odd scrawl in the corner that says \"Polly wants a ↑→→↑\"."
)

notebook_glowing = Item(
    'notebook (glowing)', 'glowing notebook', 'notebook',
    def_name='the glowing notebook',
    description="A notebook with a cloverleaf on the cover. It's now glowing? It contains many pages of cryptic writing. One page has a to-do list on it with a few items. One is a note to not forget to put the rug back before leaving. Another is a reminder to buy more crackers. Another is a reminder to call home. There's also on odd scrawl in the corner that says \"Polly wants a ↑→→↑\". There is some new glowing text that says \"Have you made the seagulls your friends yet?\"..."
)

shelf_1 = Item(
    'shelf',
    def_name='the shelf',
    description="A simple wooden shelf. There are some boxes of what looks like dried crackers on it."
)

shelf_2 = Item(
    'shelf',
    def_name='the shelf',
    description="A simple wooden shelf. There appears to be a red button behind the shelf."
)

red_button = Item(
    'button', 'red button',
    def_name='the red button',
    description="A red button mounted to the wall behind the shelf."
)

cracker_boxes = Item(
    'cracker boxes', 'cardboard', 'cardboard boxes', 'boxes', 'crackers',
    def_name='the boxes of crackers',
    description="A few boxes of dried crackers."
)

cat_poster = Item(
    'cat poster', 'poster',
    def_name='the cat poster',
    description="A cat poster. It features a cat hanging on a ledge and the caption is \"Hang in there\"... The cat looks genuinely terrified!"
)

flight_ticket = Item(
    'flight ticket', 'ticket',
    def_name='the flight ticket',
    description="A flight ticket. The departure and destination are oddly blank. The departure time is 5PM and the arrival is marked as 3AM..."
)

paintings = Item(
    'paintings', 'painting',
    def_name='the paintings',
    description="A set of fancy paintings hang on the wall. One depicts a serene beach with soft gentle waves, with an orange sun umbrella in the forground. One depicts an elegant stone church with stained glass windows and blue door. One depicts a middle aged man in an overcoat, with a rugged face and glasses sitting on a red sofa."
)

stickies = Item(
    'stickies', 'sticky notes', 'sticky', 'sticky note',
    def_name='the stickies',
    description="A set of three sticky notes with writing on them. One has \"I already took a sip. It tastes like copper\" written on it. One has \"The coffee is cold\" written on it, with a star marked in the corner. One has a number written on it - 438.796.4311. One has \"The plumber did not answer\" written on it."
)

computer = Item(
    'computer',
    def_name='the computer',
    description="A yellowing beige computer and its CRT monitor sit on the desk. The monitor's convex screen is covered in dust. A ball mouse rests beside a worn keyboard."
)

computer_on = Item(
    'computer',
    def_name='the computer',
    description="A yellowing beige computer and its CRT monitor sit on the desk. The screen shows the log in screen. The wallpaper for the login screen is very interesting. It depicts scores of pigeons escaping from a cage. There are three pigeons still in the cage, with five perched nearby, and eight flying off into the distance..."
)

filing_cabinet = Item(
    'filing cabinet', 'filing', 'cabinet',
    def_name='the filing cabinet',
    description="A dented metal filing cabinet with chipped olive-green paint stands against the wall. You try to look into each drawer and all but the bottom drawer are locked. The bottom drawer seems to be filled with junk. You find a band poster in there though, and it looks pretty cool so you take it..."
)

filing_cabinet_taken = Item(
    'filing cabinet', 'filing', 'cabinet',
    def_name='the filing cabinet',
    description="A dented metal filing cabinet with chipped olive-green paint stands against the wall. All but the bottom drawer are locked. The bottom drawer seems to be filled with junk."
)

band_poster = Item(
    'band poster', 'poster',
    def_name='the band poster',
    description="A band poster for a band called \"The Glockenspielers\". The caption says \"What the Bell are you waiting for? The Bells are tolling now!\". You can't tell if it's a joke band or serious..."
)

area_rug = Item(
    'rug', 'area rug',
    def_name='the area rug',
    description="An area rug covers much of the floor. It is a deep red and has intricate elegant lines traversing its surface."
)

area_rug_moved = Item(
    'rug', 'area rug',
    def_name='the area rug',
    description="An area rug covers much of the floor. It is a deep red and has intricate elegant lines traversing its surface. You have flipped over one of the corners of the rug, revealing a safe hidden under the rug."
)

safe = Item(
    'safe', 'keypad',
    def_name='the safe',
    description="A heavy metal safe that was hidden under the rug. It is set into the floor. It has a keypad on the front."
)

safe_open = Item(
    'safe', 'keypad',
    def_name='the open safe',
    description="A heavy metal safe that was hidden under the rug. It is set into the floor. You have already opened it and taken the contents."
)

bunny = Item(
    'bunny', 'bunny figurine', 'figurine',
    def_name='the bunny figurine',
    description="A small plastic bunny figuring. It looks pretty normal. On the bottom, it looks like someone has written a \"T\"?"
)


"""
rooms.py
"""
dark_room = Room(
    functional_description=lambda self: (
        "You are in a simple bedroom. There is a bed against the wall with a bedside table beside it."
        + (" There is an old wooden wardrobe in the corner of the room that has a secret passage inside it." if wardrobe_found_secret in list(self.fixtures) else "")
        + (" There is an old wooden wardrobe in the corner of the room. You feel oddly drawn to it..." if (wardrobe_with_secret in list(self.fixtures) or wardrobe_with_secret_investigated in list(self.fixtures)) else "")
        + (" There is an old wooden wardrobe in the corner of the room." if (wardrobe in list(self.fixtures) or wardrobe_investigated in list(self.fixtures)) else "")
        + " There is a door to the north."
    ),
    is_dark=True,
    dark_safe_exit=Direction.NORTH,
    dark_description="You are in a pitch dark room. You can just make out a faint line of light coming from under a doorway to the north. You don't feel comfortable navigating the room in the dark.",
    fixtures=[wardrobe, bed, bedside],
    room_aliases=["bedroom", "wardrobe room"]
)

secret_room = Room(
    is_dark=True,
    dark_description="You've gone into the opening, but it's very dark inside... You can't see much other than the light coming back from the opening.",
    functional_description=lambda self: (
        "Looking around with the flashlight, you can see a sparsely furnished room."
        + (" There is a small cot to one side and a shelf that looks to have many cardboard boxes on it." if cracker_boxes in list(self.items) else " There is a small cot to one side and a shelf that is now empty.")
        + " On the far side of the room to you is a small metal table with a cushioned chair."
        + ("It looks like there's something on the table." if shelf_1 in list(self.fixtures) else "")
    ),
    fixtures=[metal_table_1, shelf_1, cushioned_chair, cot],
    items=[cracker_boxes],
    room_aliases=["secret", "secret room"]
)

south_hallway = Room(
    first_time_description="You step into a narrow, dimly lit hallway. The air is damp and musty, and the walls are lined with old, peeling wallpaper. The hallway stretches off to the north. There is a door to the south.",
    static_description="You are in a narrow hallway, dimly lit by a single bulb. The hallway stretches off to the north. There is a door to the south.",
    room_aliases=["south hall", "south hallway"]
)

north_hallway = Room(
    static_description="You are in a narrow, well lit, hallway. There is a door to the north, and another door to the east. The hallway stretches off to the south.",
    room_aliases=["north hall", "north hallway"]
)

east_hallway = Room(
    functional_description=lambda self: (
        "You are in a narrow hallway, dimly lit by a few sparse bulbs."
        + (" On the floor you can see what appears to be an empty tin can." if empty_can in list(self.items) else "")
        + " There is a door to the east. The hallway stretches off to the west."
    ),
    items=[empty_can],
    room_aliases=["east hall", "east hallway"]
)

metal_gate = LockedExit("There is no handle for the metal gate. You try pushing and pulling on it but nothing seems to happen.", unlock_item=None)
heavy_wooden_door = LockedExit("You try the door, but it seems to be locked tight. You notice a small keyhole just below the handle.", unlock_item=key)

west_hallway = Room(
    functional_description=lambda self: (
        "You are in a narrow, well lit, hallway. There is a heavy-looking wooden door to the west, and an iron gate to the south."
        + (" You notice that the iron gate looks to be slightly ajar..." if not metal_gate.is_locked else "")
        + " The hallway stretches off to the east."
    ),
    locked_exits={
        Direction.WEST: heavy_wooden_door,
        Direction.SOUTH: metal_gate
    },
    room_aliases=["west hall", "west hallway"]
)

central_hallway = Room(
    functional_description=lambda self: (
        "You are in an intersection of hallways. There are hallways to the north, south, east, and west. The hallways seem brighter to the west and north than to the south and east."
        + (" It looks like there is something on the floor in the distance of the east hallway." if empty_can in list(east_hallway.items) else "")
        + (" As you are looking around you see something move in the shadows in your peripheral vision. Looking closer, you don't seem to see anything?" if game_state.CAT_HIDDEN and not game_state.CAT_OBTAINED else "")
        + (" In the shadows you see big reflective green eyes staring at you." if not game_state.CAT_HIDDEN and not game_state.CAT_OBTAINED else "")
        + (" There is a cat at your feet, purring and happily eating the food from the can." if cat in list(self.items) else "")
    ),
    room_aliases=["central hall", "central hallway", "centre hall", "centre hallway", "intersection hall", "intersection hallway", "intersection"]
)

gated_hallway = Room(
    functional_description=lambda self: (
        "You are in a narrow, well lit, hallway. The ground seems to be sloping upwards. There is a metal gate to the north and sturdy metal door to the south. There seems to be light coming from behind the door to the south."
    ),
    room_aliases=["gated hall", "gated hallway", "gate hall", "gate hallway"]
)

supply_closet = Room(
    functional_description=lambda self: (
        "You are in a cramped supply closet. Various supplies are stored on shelving along the walls, or stacked in haphazard piles. On the far wall there is a cat poster and a small metal panel door."
        + (" The panel seems lightly ajar." if breaker_closed not in list(self.fixtures) else "")
    ),
    fixtures=[breaker_closed, supplies, cat_poster],
    room_aliases=["supply closet", "supplies closet", "supply", "supplies", "closet"]
)

storage_room = Room(
    functional_description=lambda self: (
        "You are in a storage room filled with crates. Some crates are labeled with strange symbols, while others are just plain wooden boxes. Some of the lightbulbs are out, casting shadows across the room and crates."
        + (" Resting on one of the crates is a worn, red crowbar." if crowbar in list(self.items) else "")
        + (" Some of the boxes have been opened." if open_crates in list(self.fixtures) else "")
        + (" There are still " + ", ".join(item.name for item in self.items) + " in the crates..." if len(self.items) > 0 else "")
    ),
    items=[crowbar],
    fixtures=[crates],
    room_aliases=["storage room", "storage"]
)

mess = Room(
    functional_description=lambda self: (
        "You are in an eating area. There are several tables and chairs arranged for dining. The room is clean and well-maintained."
        + (" It looks like there is something on one of the tables in the middle of the room." if unobtainable_brass_key not in list(self.items) and table in list(self.fixtures) else "")
        + (" It looks like there is a small brass key on one of the tables in the middle of the room." if unobtainable_brass_key in list(self.items) else "")
        + (" In one of the corners you see a small vent." if vent in list(self.fixtures) or vent_empty in list(self.fixtures) else "")
        + " There is a door to the south and a door to the west."
    ),
    is_dark=True,
    dark_safe_exit=Direction.WEST,
    dark_description="You are in a pitch dark room. You can just make out a faint line of light coming from under a doorway to the west. You don't feel comfortable navigating the room in the dark.",
    fixtures=[table],
    room_aliases=["eating room", "eating area", "dining room", "mess hall", "mess", "dining", "eating"]
)

kitchen = Room(
    functional_description=lambda self: (
        "You are in a small kitchen. Basic appliances line the cramped space. A fridge hums quietly against one wall."
        + (" On the counter you notice an unopened can of food and a flashlight." if closed_can in list(self.items) and flashlight_dead in list(self.items) else "")
        + (" On the counter you notice an unopened can of food." if closed_can in list(self.items) and flashlight_dead not in list(self.items) else "")
        + (" On the counter you notice a flashlight." if closed_can not in list(self.items) and flashlight_dead in list(self.items) else "")
    ),
    items=[flashlight_dead, closed_can],
    fixtures=[fridge],
    room_aliases=["kitchen", "cooking area", "cooking room"]

)

office = Room(
    functional_description=lambda self: (
        "You are in what appears to be an office. There is a desk with a computer terminal as well as several filing cabinets."
        + (" The computer is off." if computer in list(self.fixtures) else " The computer is on.")
        + (" There are some sticky notes on the desk and some kind of ticket sitting one of the filing cabinets." if stickies in list(self.items) and flight_ticket in list(self.items) else "")
        + (" There are some sticky notes on the desk." if stickies in list(self.items) and flight_ticket not in list(self.items) else "")
        + (" There is some kind of ticket sitting one of the filing cabinets." if stickies not in list(self.items) and flight_ticket in list(self.items) else "")
        + " There are some fancy paintings on the wall, and the hardwood floor has a large area rug covering a large section of it."
        + (" The corner of the rug is flipped over, revealing a safe hidden under the rug." if safe in list(self.fixtures) else "") 
        +" The room gives off an elegant and sophisticated air."
    ),
    fixtures=[computer, filing_cabinet, area_rug, paintings],
    items=[stickies, flight_ticket],
    room_aliases=["office", "computer room"]
)

# 5x5 Beach Room Grid

# 0,0
beach_nw_nw = Room(
    static_description="You are standing on the beach. Small pieces of driftwood are scattered in the sand at your feet. The beach seems to stretch off as far off into the distance as you can see to the north and west. The sound of waves is more distant here, creating a peaceful atmosphere.",
    illegal_direction_description={
        Direction.NORTH: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
        Direction.WEST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 0,1
beach_nw_n = Room(
    static_description="You are standing on the beach. The sand is slightly cooler underfoot. A few seagull feathers are scattered nearby. The beach seems to stretch off as far off into the distance as you can see to the north. You can hear the faint cry of seabirds in the distance.",
    illegal_direction_description={
        Direction.NORTH: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 0,2
beach_n_n = Room(
    static_description="You are standing on the beach. Small weathered shells rest in the sand at your feet. The beach seems to stretch off as far off into the distance as you can see to the north. A gentle breeze carries the salt air from the distant waves.",
    illegal_direction_description={
        Direction.NORTH: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 0,3
beach_ne_n = Room(
    static_description="You are standing on the beach. Beach grass sways gently in the wind around you. The beach seems to stretch off as far off into the distance as you can see to the north. The sound of distant waves provides a soothing backdrop.",
    illegal_direction_description={
        Direction.NORTH: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 0,4
beach_ne_ne = Room(
    functional_description=lambda self: (
        "You are standing on the beach."
        + (" There are some seagulls nearby." if "seagulls" in self.fixtures else "") # Must be "if "seagulls" in self.fixtures" for unknown reasons
        + " The beach seems to stretch off as far off into the distance as you can see to the north and east."
    ),
    illegal_direction_description={
        Direction.NORTH: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
        Direction.EAST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    },
    fixtures=[seagulls],
    room_aliases=["seagull", "seagulls"]
)

# 1,0
beach_nw_w = Room(
    static_description="You are standing on the beach. The beach seems to stretch off as far off into the distance as you can see to the west. The sand here has a slightly different texture, mixed with small pebbles.",
    illegal_direction_description={
        Direction.WEST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 1,1
beach_nw = Room(
    static_description="You are standing on the beach. Colorful shells are mixed into the sand at your feet. The area feels sheltered, with dunes rising slightly to form natural windbreaks. You can see the door back to underground to the southeast"
)

# 1,2
beach_n = Room(
    static_description="You are standing on the beach. Sun-bleached shells and small stones rest at your feet. The sand here is fine and warm. You can see the door back to underground to the south and a shed to the southeast."
)

# 1,3
beach_ne = Room(
    static_description="You are standing on the beach. Small pieces of sun-bleached coral are scattered at your feet. This area seems to be a favorite spot for shore birds, judging by the numerous tracks in the sand heading northeast. You can see the door back to underground to the southwest and a shed to the south."
)

# 1,4
beach_ne_e = Room(
    static_description="You are standing on the beach. The sun feels particularly glaring in this part of the beach. The beach seems to stretch off as far off into the distance as you can see to the east. You can see a shed to the southwest.",
    illegal_direction_description={
        Direction.EAST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 2,0
beach_w_w = Room(
    static_description="You are standing on the beach. The beach seems to stretch off as far off into the distance as you can see to the west. Small beach flowers grow in patches between the sand dunes.",
    illegal_direction_description={
        Direction.WEST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 2,1
beach_w = Room(
    static_description="You are standing on the beach. The sand here is particularly fine and warm. You can see the door back to underground to the east."
)

# 2,2 - Your existing outside_door
outside_door = Room(
    first_time_description="You step out into the glaring light of day. As your eyes adjust, you see deep blue water off in the distance and the muted sound of waves crashing against the shore fills your ears. The small concrete pad you stand on appears to be above the tide line. Looking around you see soft white sand stretching out in every direction. You see a small wooden shed off to the east. The door back to the underground is here.",
    static_description="You are outside on a sandy beach. There is a small concrete pad with the door back to the underground here. You see a small wooden shed off to the east.",
    room_aliases=["beach", "outside", "outside door", "beach door"]
)

# 2,3 - Your existing outside_shed
outside_shed = Room(
    static_description="You are beside a small wooden shed on a sandy beach. The shed has a worn-looking roof and weathered wooden walls. It has a wooden door and a small window on one side. You can see the door back to underground to the west.",
    fixtures=[window_outside]
)

# 2,4
beach_e_e = Room(
    static_description="You are standing on the beach. The beach seems to stretch off as far off into the distance as you can see to the east. You can see a shed to the west.",
    illegal_direction_description={
        Direction.EAST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 3,0
beach_sw_w = Room(
    static_description="You are standing on the beach. Small tide pools have formed in rocky depressions at your feet. The beach seems to stretch off as far off into the distance as you can see to the west. Tiny hermit crabs scurry between the pools.",
    illegal_direction_description={
        Direction.WEST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 3,1
beach_sw = Room(
    static_description="You are standing on the beach. The sand here forms gentle ripples, evidence of the tide's artistic work. You can see the door back to underground to the northeast."
)

# 3,2
beach_s = Room(
    static_description="You are standing on the beach. Salt crystals glisten in the sand where seawater has evaporated. This area feels particularly peaceful. You can see the door back to underground to the north and a shed to the northeast."
)

# 3,3
beach_se = Room(
    static_description="You are standing on the beach. The sand here is mixed with fine shell dust, giving it a pearl-like shimmer. You can see the door back to underground to the northwest and a shed to the north."
)

# 3,4
beach_se_e = Room(
    static_description="You are standing on the beach. Smooth stones worn by countless tides rest at your feet. The beach seems to stretch off as far off into the distance as you can see to the east. You can see a shed to the northeast.",
    illegal_direction_description={
        Direction.EAST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
    }
)

# 4,0
beach_sw_sw = Room(
    static_description="You are standing on the beach with the ocean directly to the south. Larger waves crash nearby and you feel the spray from the waves. The beach seems to stretch off as far off into the distance as you can see to the west.",
    illegal_direction_description={
        Direction.WEST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
        Direction.SOUTH: "The ocean looks pretty wet. You don't really feel like swimming...",
    }
)

# 4,1
beach_sw_s = Room(
    static_description="You are standing on the beach with the ocean directly to the south. The ocean waves roll almost to your feet. Foam and seaweed create intricate patterns in the wet sand around you.",
    illegal_direction_description={
        Direction.SOUTH: "The ocean looks pretty wet. You don't really feel like swimming...",
    }
)

# 4,2
beach_s_s = Room(
    static_description="You are standing on the beach with the ocean directly to the south. The rolling waves of the ocean come close to your position. You see fish in the water near you.",
    illegal_direction_description={
        Direction.SOUTH: "The ocean looks pretty wet. You don't really feel like swimming...",
    }
)

# 4,3
beach_se_s = Room(
    static_description="You are standing on the beach with the ocean directly to the south. The ocean seems peaceful here. There are bits of seaweed scattered in the sand at your feet.",
    illegal_direction_description={
        Direction.SOUTH: "The ocean looks pretty wet. You don't really feel like swimming...",
    }
)

# 4,4
beach_se_se = Room(
    static_description="You are standing on the beach with the ocean directly to the south. Some crabs skitter about in the sand.",
    illegal_direction_description={
        Direction.EAST: "The beach seems to stretch on forever. It's probably not a good idea to venture too far...",
        Direction.SOUTH: "The ocean looks pretty wet. You don't really feel like swimming...",
    }
)

shed = Room(
    functional_description=lambda self: (
        "You are inside a small wooden shed. It's dimly lit by a single small window. The walls are lined with maps and nautical memorabilia."
        + (" There is a workbench off to the side and it looks like it has a phone and some papers scattered about." if papers in list(self.items) else " There is a workbench off to the side and it looks like it has a phone on it.")
    ),    
    fixtures=[window_inside, phone, maps, workbench, nautical_memorabilia],
    items=[papers],
    room_aliases=["shed", "phone room"]
)

all_rooms = (dark_room, secret_room, south_hallway, north_hallway, east_hallway, west_hallway, central_hallway, gated_hallway, supply_closet, storage_room, mess, kitchen, office, beach_nw_nw, beach_nw_n, beach_n_n, beach_ne_n, beach_ne_ne, beach_nw_w, beach_nw, beach_n, beach_ne, beach_ne_e, beach_w_w, beach_w, outside_door, outside_shed, beach_e_e, beach_sw_w, beach_sw, beach_s, beach_se, beach_se_e, beach_sw_sw, beach_sw_s, beach_s_s, beach_se_s, beach_se_se, shed)

def get_room_aliases():
    """Set up room aliases for easier access."""
    room_aliases = {}
    for room in all_rooms:
        for alias in room.room_aliases:
            room_aliases[alias.lower()] = room

    return room_aliases

# Room connections
def setup_room_connections():
    """Set up all room connections."""
    central_hallway.south = south_hallway
    central_hallway.north = north_hallway
    central_hallway.east = east_hallway
    central_hallway.west = west_hallway

    north_hallway.east = supply_closet
    north_hallway.north = storage_room

    south_hallway.south = dark_room

    east_hallway.east = mess
    mess.south = kitchen

    west_hallway.west = office
    west_hallway.south = gated_hallway

    # Outside beach grid connections
    # Row 0 connections
    beach_nw_nw.east = beach_nw_n
    beach_nw_nw.south = beach_nw_w

    beach_nw_n.west = beach_nw_nw
    beach_nw_n.east = beach_n_n
    beach_nw_n.south = beach_nw

    beach_n_n.west = beach_nw_n
    beach_n_n.east = beach_ne_n
    beach_n_n.south = beach_n

    beach_ne_n.west = beach_n_n
    beach_ne_n.east = beach_ne_ne
    beach_ne_n.south = beach_ne

    beach_ne_ne.west = beach_ne_n
    beach_ne_ne.south = beach_ne_e

    # Row 1 connections
    beach_nw_w.north = beach_nw_nw
    beach_nw_w.east = beach_nw
    beach_nw_w.south = beach_w_w

    beach_nw.north = beach_nw_n
    beach_nw.west = beach_nw_w
    beach_nw.east = beach_n
    beach_nw.south = beach_w

    beach_n.north = beach_n_n
    beach_n.west = beach_nw
    beach_n.east = beach_ne
    beach_n.south = outside_door

    beach_ne.north = beach_ne_n
    beach_ne.west = beach_n
    beach_ne.east = beach_ne_e
    beach_ne.south = outside_shed

    beach_ne_e.north = beach_ne_ne
    beach_ne_e.west = beach_ne
    beach_ne_e.south = beach_e_e

    # Row 2 connections
    beach_w_w.north = beach_nw_w
    beach_w_w.east = beach_w
    beach_w_w.south = beach_sw_w

    beach_w.north = beach_nw
    beach_w.west = beach_w_w
    beach_w.east = outside_door
    beach_w.south = beach_sw

    outside_door.north = beach_n
    outside_door.west = beach_w
    outside_door.east = outside_shed
    outside_door.south = beach_s

    outside_shed.north = beach_ne
    outside_shed.west = outside_door
    outside_shed.east = beach_e_e
    outside_shed.south = beach_se

    beach_e_e.north = beach_ne_e
    beach_e_e.west = outside_shed
    beach_e_e.south = beach_se_e

    # Row 3 connections
    beach_sw_w.north = beach_w_w
    beach_sw_w.east = beach_sw
    beach_sw_w.south = beach_sw_sw

    beach_sw.north = beach_w
    beach_sw.west = beach_sw_w
    beach_sw.east = beach_s
    beach_sw.south = beach_sw_s

    beach_s.north = outside_door
    beach_s.west = beach_sw
    beach_s.east = beach_se
    beach_s.south = beach_s_s

    beach_se.north = outside_shed
    beach_se.west = beach_s
    beach_se.east = beach_se_e
    beach_se.south = beach_se_s

    beach_se_e.north = beach_e_e
    beach_se_e.west = beach_se
    beach_se_e.south = beach_se_se

    # Row 4 connections
    beach_sw_sw.north = beach_sw_w
    beach_sw_sw.east = beach_sw_s

    beach_sw_s.north = beach_sw
    beach_sw_s.west = beach_sw_sw
    beach_sw_s.east = beach_s_s

    beach_s_s.north = beach_s
    beach_s_s.west = beach_sw_s
    beach_s_s.east = beach_se_s

    beach_se_s.north = beach_se
    beach_se_s.west = beach_s_s
    beach_se_s.east = beach_se_se

    beach_se_se.north = beach_se_e
    beach_se_se.west = beach_se_s

# Initialize room connections
setup_room_connections()

room_aliases = get_room_aliases()


'''
game_state.py
'''
def set_state_flag(item_obj):
    if item_obj == band_poster:
        game_state.OFFICE_POSTER = True
    elif item_obj == stickies:
        game_state.OFFICE_STICKIES = True
    elif item_obj == paintings:
        game_state.OFFICE_PAINTINGS = True
    elif item_obj == flight_ticket:
        game_state.OFFICE_TICKET = True
    else:
        return

    check_if_all_office_collected()

def check_if_all_office_collected():
    if game_state.OFFICE_POSTER and game_state.OFFICE_STICKIES and game_state.OFFICE_PAINTINGS and game_state.OFFICE_TICKET and game_state.OFFICE_COMPUTER:
        ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.OFFICE_ALL_FOUND] = "true"
        controller_wardrobe()

'''
app.py
'''
SAFE_NUMBER: str = '93247'

RESPONSE_UNKNOWN = "I don't understand that. If you need help, just ask me to 'explain'."

class ADDITIONAL_STATE_KEYS(str, Enum):
    CALL_WITH_HINT = "call_with_hint"
    HINT_INDEX = "hint_index"
    SEAGULLS_FOUND = "seagulls_found"

    # State specific to long-term mode
    OFFICE_ALL_FOUND = "office_all_found"

ADDITIONAL_STATE_TO_RESPOND: dict[ADDITIONAL_STATE_KEYS, str] = {}

# Manually set debug mode
debug_mode = True

# Manually set if early-access mode or not
early_access_mode = False

phone_validator = None

# --- Game Setup ---
current_room: Room = dark_room
inventory = Bag()
set_context(Context.EXPLORING)


@when("PHONE", context=Context.USING_PHONE)
def phone_number(phone):
    set_context(Context.EXPLORING)
    ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.CALL_WITH_HINT] = phone
    ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.HINT_INDEX] = str(random.randint(0, 1))

    return "You call the number..."


@when("DIGITS", context=Context.USING_SAFE)
def using_safe(digits):
    global SAFE_NUMBER, current_room

    stripped_digits = digits.strip()

    if not stripped_digits.isdigit():
        return "I can only enter digits..."
    
    if len(stripped_digits) != 5:
        return "I can only enter five digits..."
    
    if stripped_digits == SAFE_NUMBER:
        set_context(Context.EXPLORING)
        current_room.fixtures.remove(safe)
        current_room.fixtures.add(safe_open)
        inventory.add(bunny)
        return "You enter the code and the safe makes a happy beep! The door swings open and inside you find a small plastic toy bunny? You take the bunny."
    else:
        set_context(Context.EXPLORING)
        return "You enter the code and the safe makes a sad bloop sound... That must not have been the code..."


@when("push button", context=Context.EXPLORING)
def push_button():
    if metal_gate.is_locked:
        metal_gate.is_locked = False
        return "You push the button. You hear a loud click, followed by a metallic creaking sound from somewhere outside."
    else:
        return "You push the button. Nothing seemed happened this time..."


@when("look", context=Context.EXPLORING)
@when("investigate", context=Context.EXPLORING)
def look_room():
    global current_room
    
    return current_room.get_description()

@when("go DIRECTION door", context=Context.EXPLORING)
def go_direction_door(direction):
    global current_room

    # Check trying to navigate a dark room
    if current_room.is_dark and direction in [d.value for d in Direction] and direction != current_room.dark_safe_exit:
        return "The room is too dark to navigate that way."

    # Handle two-door rooms specially
    if current_room == mess:
        if direction == Direction.WEST:
            return go(Direction.WEST)
        elif direction == Direction.SOUTH:
            return go(Direction.SOUTH)
        else:
            return "There is no door that way."
    elif current_room == north_hallway:
        if direction == Direction.EAST:
            return go(Direction.EAST)
        elif direction == Direction.NORTH:
            return go(Direction.NORTH)
        else:
            return "There is no door that way."
    else:
        return go("door") # Yes I reallize this isn't totally correct, but it is a bit better for the user if they make a mistake...


@when("move rug", context=Context.EXPLORING)
@when("move area rug", context=Context.EXPLORING)
@when("check under rug", context=Context.EXPLORING)
@when("check under area rug", context=Context.EXPLORING)
@when("look under rug", context=Context.EXPLORING)
@when("look under area rug", context=Context.EXPLORING)
def move_rug():
    global current_room

    if current_room == office and area_rug in list(current_room.fixtures):
        current_room.fixtures.remove(area_rug)
        current_room.fixtures.add(area_rug_moved)
        current_room.fixtures.add(safe)
        return "You flip over one of the corner of the rug. Hidden underneath, you find a safe set into the floor..."
    else:
        return "The rug is already flipped over. Hidden underneath is a safe set into the floor..."


@when("go DIRECTION", context=Context.EXPLORING)
@when("move DIRECTION", context=Context.EXPLORING)
def go(direction):
    global current_room

    # Handling for quick navigation by room name
    if direction in room_aliases:
        new_room = room_aliases[direction]
        if new_room == current_room:
            return "You are already here."
        else:
            if debug_mode or not new_room.first_time_in_room:
                current_room = room_aliases[direction]                
                return "You walk back to the " + direction + ". " + current_room.get_description()
            else:
                return "You can't go that way."

    # Check trying to navigate a dark room
    if current_room.is_dark and direction in [d.value for d in Direction] and direction != current_room.dark_safe_exit:
        return "The room is too dark to navigate that way."
    
    # Special handling for SOUTH at gated_hallway as NORTH at outside_door is different
    if current_room == gated_hallway and direction == Direction.SOUTH:
        current_room = outside_door
        return current_room.get_description()

    # Check if trying to go to the 'gate'
    if direction == 'gate' or direction == 'metal gate':
        if current_room == west_hallway:
            direction = Direction.SOUTH
        elif current_room == gated_hallway:
            direction = Direction.NORTH
        else:
            return "There is no gate here."

    # Check if trying to go to a 'door'
    if direction == 'door':
        if current_room == dark_room:
            direction = Direction.NORTH
        elif current_room == south_hallway:
            direction = Direction.SOUTH
        elif current_room == east_hallway:
            direction = Direction.EAST
        elif current_room == kitchen:
            direction = Direction.NORTH
        elif current_room == west_hallway:
            direction = Direction.WEST
        elif current_room == office:
            direction = Direction.EAST
        elif current_room == supply_closet:
            direction = Direction.WEST
        elif current_room == storage_room:
            direction = Direction.SOUTH
        elif current_room == gated_hallway:
            current_room = outside_door
            return current_room.get_description()
        elif current_room == outside_door:
            current_room = gated_hallway
            return current_room.get_description()
        elif current_room == outside_shed:
            current_room = shed
            return current_room.get_description()
        elif current_room == shed:
            current_room = outside_shed
            return current_room.get_description()
        elif current_room == mess or current_room == north_hallway:
            return "Which door do you mean? There are two doors here."
        else:
            return "There is no door here."

    # Handling for going underground
    if direction == 'underground' and current_room == outside_door:
        current_room = gated_hallway
        return current_room.get_description()

    # Check trying to enter the wardrobe
    if wardrobe_found_secret in list(current_room.fixtures) and direction in ['wardrobe', 'darkness', 'opening', 'inside']:
        current_room = secret_room
        return current_room.get_description()
    
    # Check trying to exit the wardrobe
    if current_room == secret_room and (direction in ['wardrobe', 'light', 'opening', 'back'] if current_room.is_dark else direction in ['wardrobe', 'opening', 'back']):
        current_room = dark_room
        return current_room.get_description()

    # Handle normal directional movement
    if direction in current_room.exits():
        # Check if seagulls need to return
        if current_room == beach_ne_ne and seagulls not in list(current_room.fixtures) and not game_state.DISCOVERED_SEAGULLS:
            current_room.fixtures.add(seagulls)

        # Check if exit is locked
        locked_exit: LockedExit|None = current_room.locked_exits.get(direction)
        if locked_exit and locked_exit.is_locked:
            return locked_exit.description
        
        current_room = current_room.exit(direction)
        return current_room.get_description()
    elif current_room.illegal_direction_description and direction in current_room.illegal_direction_description.keys():
        return current_room.illegal_direction_description[direction]
    else:
        return "You can't go that way."


@when("investigate ITEM", context=Context.EXPLORING)
@when("look ITEM", context=Context.EXPLORING)
@when("look at ITEM", context=Context.EXPLORING)
def look_item(item):
    global current_room

    # Check trying to do things in a dark room
    if current_room.is_dark:
        return "The room is too dark to do anything."
    
    inv_item = inventory.find(item)
    room_item = current_room.items.find(item)
    fixture = current_room.fixtures.find(item)
    if inv_item:
        set_state_flag(inv_item)
        return inv_item.description
    if room_item:
        set_state_flag(room_item)
        return room_item.description
    if fixture:
        set_state_flag(fixture)
        if fixture == table:
            current_room.items.add(unobtainable_brass_key)
        if fixture == wardrobe_with_secret:
            current_room.fixtures.remove(wardrobe_with_secret)
            current_room.fixtures.add(wardrobe_found_secret)
        if fixture == wardrobe_with_secret_investigated:
            current_room.fixtures.remove(wardrobe_with_secret_investigated)
            current_room.fixtures.add(wardrobe_found_secret)
        if fixture == metal_table_1:
            current_room.items.add(notebook)
        if fixture == fridge:
            current_room.items.add(sandwich)
        if fixture == filing_cabinet:
            current_room.fixtures.remove(filing_cabinet)
            current_room.fixtures.add(filing_cabinet_taken)
            inventory.add(band_poster)

        return fixture.description
    
    return f"There is no {item} around..."


@when("take ITEM", context=Context.EXPLORING)
def take_item(item):
    global current_room

    # Check trying to do things in a dark room
    if current_room.is_dark:
        return "The room is too dark to do anything."

    room_item = current_room.items.find(item)
    fixture = current_room.fixtures.find(item)
    
    if fixture:
        if fixture == area_rug:
            return move_rug()
        
        if fixture == seagulls:
            current_room.fixtures.remove(seagulls)
            return "The seagulls fly away as you approach them."
        
        return f"You can't take the {item}."
    
    if room_item:
        if room_item == unobtainable_brass_key:
            current_room.items.remove(unobtainable_brass_key)
            current_room.fixtures.remove(table)
            current_room.fixtures.add(vent)
            return "While you were contemplating taking the key, a mouse ran up and took the key! It ran off into a vent in the corner of the room."
        
        if room_item == cracker_boxes:
            current_room.items.remove(cracker_boxes)
            inventory.add(cracker_boxes)
            current_room.fixtures.remove(shelf_1)
            current_room.fixtures.add(shelf_2)
            current_room.fixtures.add(red_button)
            return "You take the boxes of crackers. As you remove them, you notice that there is a red button on the wall behind where the boxes of crackers were."

        if room_item == notebook:
            current_room.fixtures.remove(metal_table_1)
            current_room.fixtures.add(metal_table_2)
        
        if room_item == sandwich:
            current_room.items.remove(sandwich)
            inventory.add(sandwich)
            current_room.fixtures.remove(fridge)
            current_room.fixtures.add(fridge_no_sand)
            return "You take the sandwich."
        
        if current_room == central_hallway:
            if not game_state.CAT_HIDDEN and not game_state.CAT_OBTAINED:
                return "When you try to take the cat, it runs away."
            if room_item == open_can:
                return "The cat is currently eating from the can. You can't take it right now."
        
        if current_room == central_hallway and room_item == cat:
            taken_cat = current_room.items.take(item)
            taken_can = current_room.items.take("open can")
            inventory.add(taken_cat)
            inventory.add(taken_can)

            return "You take the cat. You also take the open can of food it was eating from. The cat seems happy to be with you and curls up in your arms, purring contentedly."

        taken_item = current_room.items.take(item)
        inventory.add(taken_item)
        return f'You take {taken_item.def_name}.'

    return f'There is no {item} here.'


@when("eat ITEM", context=Context.EXPLORING)
def eat_item(item):
    global current_room

    # Check trying to do things in a dark room
    if current_room.is_dark:
        return "The room is too dark to do anything."
    
    inv_item = inventory.find(item)

    if inv_item:
        if inv_item == sandwich:
            inventory.remove(sandwich)
            return "You rip into the sandwich eagerly. Each bite is a perfect combination of flavors and textures—savory meat, tangy cheese, fresh vegetables. Before you know it, you've finished every last crumb. You feel refreshed and energized."
        if inv_item == cracker_boxes:
            return "You open the boxes of crackers. You munch on a few of the crackers and find them tasty, though a bit stale."
        if inv_item == open_can:
            return "You don't really want to eat mushy food. It's not very appetizing."
        if inv_item == dry_rations:
            inventory.remove(dry_rations)
            return "You eat the dry rations. They are very stale, and you don't feel very satisfied."
        
        return f"You can't eat {item}."

    return f"You don't have {item}."


@when("unlock door", context=Context.EXPLORING)
def unlock_door():
    global current_room
    obj = inventory.find("key")
    if not obj:
        return f"You do not have a key."
    
    if current_room == west_hallway:
        inventory.remove(obj)
        heavy_wooden_door.is_locked = False
        return "You unlock the heavy-looking wooden door."

    return "There is nowhere to use your key."


@when("use ITEM on FIXTURE", context=Context.EXPLORING)
def use_item_on_fixture(item, fixture):
    global current_room

    inv_item = inventory.find(item)
    obj_item = current_room.fixtures.find(fixture) or inventory.find(fixture)

    if not inv_item:
        return f"You do not have {item}."

    if not obj_item:
        if inv_item == key:
            if current_room == west_hallway and (fixture.strip() == 'door' or fixture.strip() == 'heavy door' or fixture.strip() == 'wooden door' or fixture.strip() == 'heavy wooden door'):
                inventory.remove(key)
                heavy_wooden_door.is_locked = False
                return "You unlock the heavy-looking wooden door."

            return "There is nowhere to use your key."

        # Special case to feed the cat
        if inv_item == open_can and current_room == central_hallway and (fixture.strip() == 'cat' or fixture.strip() == 'shadow'):
            game_state.CAT_HIDDEN = False
            game_state.CAT_OBTAINED = True
            current_room.items.add(cat)
            current_room.items.add(open_can)
            inventory.remove(open_can)
            return "You put the open can on the ground. A fluffy gray cat comes running over and starts happily eating the food. It looks up at you with big green eyes, and then goes back to eating."

        return f"There is no {fixture} here."

    if inv_item == crowbar:
        if obj_item == breaker_closed:
            current_room.fixtures.remove(breaker_closed)
            current_room.fixtures.add(breaker_open)
            return "You pry open the metal panel with the crowbar. Inside you see a circuit breaker. It looks like all of the circuit breakers are in the 'on' position except for one."
        if obj_item == breaker_open or obj_item == breaker_open_and_on:
            return "The panel is already open."
        if obj_item == crates:
            current_room.fixtures.remove(crates)
            current_room.fixtures.add(open_crates)
            current_room.items.add(stuffie)
            current_room.items.add(dry_rations)
            current_room.items.add(batteries)
            return "You pry open some wooden crates with the crowbar. Inside you find a cute stuffie, dry rations, and a few batteries. You are feeling tired and don't want to open any more crates right now."
        if obj_item == open_crates:
            return "You are feeling tired and don't want to open any more crates right now."
        if obj_item == vent or obj_item == vent_empty:
            return "You could probably use the crowbar to pry off the vent cover. You don't think you'd be able to fit into it even without the vent cover. It's probably best to leave it alone."
        else:
            return "You can't use the crowbar on that."
        
    if inv_item == cat:
        if obj_item == vent:
            inventory.add(unobtainable_brass_key)
            current_room.fixtures.remove(vent)
            current_room.fixtures.add(vent_empty)
            return "The cat dashes into the vent! You hear a commotion inside. After a moment, the cat comes back out, proudly carrying a small brass key in its mouth. It drops the key at your feet. You retrieve the key, and your friendly feline companion."
        if obj_item == vent_empty:
            return "The cat doesn't seem to want to go back into the vent."
        
    if inv_item == cracker_boxes:
        if obj_item == cat:
            return "The cat doesn't seem interested in crackers."
        if obj_item == seagulls:
            game_state.DISCOVERED_SEAGULLS = True
            ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.SEAGULLS_FOUND] = "True"
            current_room.fixtures.remove(seagulls)
            return "You take a handfull of crackers and toss them lightly towards the birds. They quickly scurry over to the crackers and begin devouring them, screeching \"MINE!\". Contented, most of them fly away - all except for one. It cranes its neck sideways before saying \"Thank you\" in a deep baritone voice. It flies away into the distance..."

    if inv_item == dry_rations:
        if obj_item == cat:
            return "The cat doesn't seem interested in the dry rations."
        if obj_item == vent:
            return "The mouse doesn't seem interested in the dry rations."
        if obj_item == seagulls:
            return "They stare blankly at you. They don't seem impressed by your offering."

    if inv_item == stuffie:
        if obj_item == notebook:
            inventory.remove(notebook)
            inventory.remove(notebook_glowing)
            return "What does that even mean? You touch the stuffie to the notebook... You're not sure what to expect by doing that, but the notebook starts to glow?"
        if obj_item == notebook_glowing:
            return "You touch the stuffie to the notebook expecting something to happen... The notebook continues steadily glowing."

    if inv_item == batteries and obj_item == flashlight_dead:
        inventory.remove(flashlight_dead)
        inventory.remove(batteries)
        inventory.add(flashlight_powered)
        return "You insert the batteries into the flashlight. It feels a bit heavier now, but you can tell it is ready to use."

    if inv_item == key:
        return "There is nowhere to use your key."

    # Special case to feed the cat
    if inv_item == open_can:
        if obj_item == cat:
            return "You feed the fluffy gray cat some food. It looks very content."

    return f"You can't use {item} on {fixture}."
        

@when("turn on", context=Context.EXPLORING)
@when("turn on breaker", context=Context.EXPLORING)
def turn_on_breaker():
    global current_room

    if current_room != supply_closet or (current_room == supply_closet and breaker_closed in list(current_room.fixtures)):
        return "There is nothing to turn on here."
    else:
        if breaker_open in list(current_room.fixtures):
            current_room.fixtures.remove(breaker_open)
            current_room.fixtures.add(breaker_open_and_on)
            dark_room.is_dark = False
            mess.is_dark = False
            return "You flip the breaker to the 'on' position."
        if breaker_open_and_on in list(current_room.fixtures):
            return "The breaker is already in the 'on' position."


@when("use ITEM", context=Context.EXPLORING)
def use_item(item):
    global current_room

    inv_item = inventory.find(item)
    fixture = current_room.fixtures.find(item)

    if item == 'switch':
        current_room.fixtures.remove(breaker_open)
        current_room.fixtures.add(breaker_open_and_on)
        dark_room.is_dark = False
        mess.is_dark = False
        return "You flip the breaker to the 'on' position."

    if fixture:
        if fixture == phone:
            if early_access_mode:
                set_context(Context.USING_PHONE)
                return "You pick up the phone. It feels heavy and old. You hear a dial tone... What number do you want to call?"
            else:
                ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.CALL_WITH_HINT] = 'arbitrary'
                ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.HINT_INDEX] = 'arbitrary'
                return "You pick up the phone. It feels heavy and old. You hear a dial tone... You feel sentimental and call home."
        if fixture == breaker_open:
            current_room.fixtures.remove(breaker_open)
            current_room.fixtures.add(breaker_open_and_on)
            dark_room.is_dark = False
            mess.is_dark = False
            return "You flip the breaker to the 'on' position."
        if fixture == safe:
            set_context(Context.USING_SAFE)
            return "You push one of the buttons on the keypad and it lights up. It seems to want you to enter five digits... What do you want to enter?"
        if fixture == safe_open:
            return "You've already opened the safe."
        if fixture == computer:
            current_room.fixtures.remove(computer)
            current_room.fixtures.add(computer_on)
            game_state.OFFICE_COMPUTER = True
            check_if_all_office_collected()
            return "You turn on the power and the whole thing hums with old cooling fans. The screen comes to life and you are at the log in screen. The wallpaper for the login screen is very interesting. It depicts scores of pigeons escaping from a cage. There are three pigeons still in the cage, with five perched nearby, and eight flying off into the distance..."
        if fixture == red_button:
            return push_button()

    if not inv_item:
        return f"You do not have {item}."

    if inv_item == flashlight_powered:
        if current_room == central_hallway:
            game_state.CAT_HIDDEN = False
            return "You shine the flashlight around." + (
                " In the shadows you see big reflective green eyes staring at you. It looks like a cat!" if cat not in list(central_hallway.items) else "")
        
        if current_room == secret_room:
            current_room.is_dark = False
            return current_room.get_description()
        
        return "It's already light enough here to see without a flashlight."

    if inv_item == flashlight_dead:
        return "you try to use the flashlight, but it appears to be dead."

    if inv_item == open_can:
        if current_room == central_hallway:
            game_state.CAT_HIDDEN = False
            game_state.CAT_OBTAINED = True
            current_room.items.add(cat)
            current_room.items.add(open_can)
            inventory.remove(open_can)
            return "You put the open can on the ground. A fluffy gray cat comes running over and starts happily eating the food. It looks up at you with big green eyes, and then goes back to eating."
        
    if inv_item == closed_can:
        return "The can isn't open..."
        
    if inv_item == stuffie:
        return "You hug the stuffie. It feels comforting and makes a soft squeak."
    
    if inv_item == cat:
        return "You hug the cat. It purrs softly and nuzzles against you."
    
    return f"You can't use {item}."


@when("open ITEM", context=Context.EXPLORING)
def open_item(item):
    global current_room

    inv_item = inventory.find(item)
    fixture = current_room.fixtures.find(item)

    if inv_item == closed_can:
        inventory.remove(closed_can)
        inventory.add(open_can)
        return "You pull the tab on the top of the can and open it. It has a brown mushy substance inside."

    if fixture == breaker_closed:
        return "You try to open the metal panel, but it's firmly shut."

    if fixture == breaker_open or fixture == breaker_open_and_on:
        return "The panel is already open."
    
    return f"You can't open {item}."


@when("inventory", context=Context.EXPLORING)
def show_inventory():
    if not inventory:
        return "You have nothing"
    for item in inventory:
        return "You have: \n" + '\n'.join(f'* {item.name}' for item in inventory)


@when("explain", context=Context.EXPLORING)
def help_cmd():
    return "You can tell me what you want to do in simple language. For example, you can 'look' or 'investigate' your surroundings or if you see something interesting like a pen you can 'investigate pen' or try to 'take pen'. If you had pen and paper, you could try to 'use pen on paper'. You can 'go north', 'go door', or 'go north door' if you want to take a door to the north. If you forget what you have, you can ask to see your 'inventory'."


def controller_wardrobe():
    if wardrobe in list(dark_room.fixtures):
        dark_room.fixtures.remove(wardrobe)
        dark_room.fixtures.add(wardrobe_with_secret)
    
    if wardrobe_investigated in list(dark_room.fixtures):
        dark_room.fixtures.remove(wardrobe_investigated)
        dark_room.fixtures.add(wardrobe_with_secret_investigated)


@when("debug phone NUMBER", context=Context.EXPLORING)
def debug_phone(number):
    phone_index = phone_validator.phone_index(number)
    return f"acknowledged - phone {number} has index {phone_index} and returned index {phone_index % 2}"


@when("debug phonecall INDEX NUMBER", context=Context.EXPLORING)
def debug_phonecall(index, number):
    ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.CALL_WITH_HINT] = number
    ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.HINT_INDEX] = str(int(index) % 2)
    return f"acknowledged - calling {number} with hint index {str(int(index) % 2)}"


# DEBUG COMMANDS
if debug_mode:
    @when("light", context=Context.EXPLORING)
    def light():
        print("DEBUG: light command triggered!")
        global current_room
        print(f"DEBUG: current_room = {current_room.get_description()}")
        
        current_room.is_dark = False
        print(f"DEBUG: current_room = {current_room.is_dark}")
        return "Let there be light!"


    @when("secret") # DEBUG COMMAND
    def secret_wardrobe():
        global current_room
        if current_room is not dark_room:
            return RESPONSE_UNKNOWN
        current_room = secret_room
        if getattr(current_room, "first_time_in_room", True):
            current_room.first_time_in_room = False
            if getattr(current_room, "first_time_description", None):
                return current_room.first_time_description
        return current_room.description

    @when("seagulls test") # DEBUG COMMAND -
    def seagulls_test():
        game_state.DISCOVERED_SEAGULLS = True
        ADDITIONAL_STATE_TO_RESPOND[ADDITIONAL_STATE_KEYS.SEAGULLS_FOUND] = "True"
        return "You take a handfull of crackers and toss them lightly towards the birds."
        

def fake_sms_reply(sender, body):
    global ADDITIONAL_STATE_TO_RESPOND, current_room, inventory, game_state
    
    try:
        result = dispatch_command(body)
    except Exception as e:
        print(f"dispatch_command error: {e}")
        result = None
    if not result:
        result = RESPONSE_UNKNOWN

    response = {
        "body": result,
        **(ADDITIONAL_STATE_TO_RESPOND if ADDITIONAL_STATE_TO_RESPOND else {})
    }

    # Clear additional state
    ADDITIONAL_STATE_TO_RESPOND = {}

    return json.dumps(response)

# Expose to JavaScript
window.fake_sms_reply = fake_sms_reply
