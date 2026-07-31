"""
On-Screen Keyboard Component
D-pad navigable keyboard for text input on Apple TV/Android TV style
"""

from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class KeyboardLayout(Enum):
    """Keyboard layout types"""
    QWERTY = "qwerty"
    NUMERIC = "numeric"
    EMAIL = "email"
    SEARCH = "search"


@dataclass
class KeyboardKey:
    """A single key on the keyboard"""
    label: str
    value: str
    row: int
    col: int
    width: int = 1  # Key width in grid units (for space bar, etc.)
    special: bool = False  # Special keys like backspace, space, done


class OnScreenKeyboard:
    """
    On-screen keyboard with D-pad navigation
    Similar to Apple TV / Android TV text input
    """
    
    # QWERTY layout (4 rows)
    QWERTY_LAYOUT = [
        # Row 0: Numbers and symbols
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        # Row 1: QWERTY top
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        # Row 2: QWERTY middle
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", "⌫"],
        # Row 3: QWERTY bottom + controls
        ["ABC", "Z", "X", "C", "V", "B", "N", "M", "@", "✓"],
    ]
    
    NUMERIC_LAYOUT = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["⌫", "0", "✓"],
    ]
    
    EMAIL_LAYOUT = [
        ["@", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", "."],
        ["ABC", "Z", "X", "C", "V", "B", "N", "M", "⌫", "✓"],
    ]
    
    SPECIAL_KEYS = {
        "⌫": "backspace",
        "✓": "done",
        "ABC": "shift",
        "123": "numeric",
        "   ": "space",
    }
    
    def __init__(
        self,
        layout: KeyboardLayout = KeyboardLayout.QWERTY,
        initial_text: str = "",
        placeholder: str = "",
        on_submit: Optional[Callable[[str], None]] = None,
    ):
        self.layout_type = layout
        self.text = initial_text
        self.placeholder = placeholder
        self.on_submit = on_submit
        
        # Cursor position on keyboard grid
        self.cursor_row = 0
        self.cursor_col = 0
        
        # Shift state
        self.shift_mode = False
        self.caps_lock = False
        
        # Load layout
        self._load_layout()
    
    def _load_layout(self):
        """Load keyboard layout based on type"""
        if self.layout_type == KeyboardLayout.QWERTY:
            layout = self.QWERTY_LAYOUT
        elif self.layout_type == KeyboardLayout.NUMERIC:
            layout = self.NUMERIC_LAYOUT
        elif self.layout_type == KeyboardLayout.EMAIL:
            layout = self.EMAIL_LAYOUT
        else:
            layout = self.QWERTY_LAYOUT
        
        # Convert to KeyboardKey objects
        self.keys: List[List[KeyboardKey]] = []
        for row_idx, row in enumerate(layout):
            key_row = []
            for col_idx, label in enumerate(row):
                key = KeyboardKey(
                    label=label,
                    value=self._get_key_value(label),
                    row=row_idx,
                    col=col_idx,
                    width=3 if label == "   " else 1,  # Space bar wider
                    special=label in self.SPECIAL_KEYS,
                )
                key_row.append(key)
            self.keys.append(key_row)
        
        self.num_rows = len(self.keys)
        self.num_cols = max(len(row) for row in self.keys)
    
    def _get_key_value(self, label: str) -> str:
        """Get the actual value to insert for a key label"""
        if label in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[label]
        return label.lower() if not (self.shift_mode or self.caps_lock) else label
    
    def get_current_key(self) -> Optional[KeyboardKey]:
        """Get the key at current cursor position"""
        if 0 <= self.cursor_row < len(self.keys):
            row = self.keys[self.cursor_row]
            if 0 <= self.cursor_col < len(row):
                return row[self.cursor_col]
        return None
    
    def move_cursor(self, direction: str) -> bool:
        """
        Move cursor in a direction
        Returns True if moved successfully
        """
        if direction == "up":
            if self.cursor_row > 0:
                self.cursor_row -= 1
                # Clamp column to new row length
                self.cursor_col = min(self.cursor_col, len(self.keys[self.cursor_row]) - 1)
                return True
        
        elif direction == "down":
            if self.cursor_row < self.num_rows - 1:
                self.cursor_row += 1
                self.cursor_col = min(self.cursor_col, len(self.keys[self.cursor_row]) - 1)
                return True
        
        elif direction == "left":
            if self.cursor_col > 0:
                self.cursor_col -= 1
                return True
            elif self.cursor_row > 0:
                # Wrap to end of previous row
                self.cursor_row -= 1
                self.cursor_col = len(self.keys[self.cursor_row]) - 1
                return True
        
        elif direction == "right":
            if self.cursor_col < len(self.keys[self.cursor_row]) - 1:
                self.cursor_col += 1
                return True
            elif self.cursor_row < self.num_rows - 1:
                # Wrap to start of next row
                self.cursor_row += 1
                self.cursor_col = 0
                return True
        
        return False
    
    def select_current_key(self) -> Optional[str]:
        """
        Select (press) the current key
        Returns action taken or None
        """
        key = self.get_current_key()
        if not key:
            return None
        
        value = key.value
        
        # Handle special keys
        if value == "backspace":
            if self.text:
                self.text = self.text[:-1]
            return "backspace"
        
        elif value == "done":
            if self.on_submit:
                self.on_submit(self.text)
            return "done"
        
        elif value == "shift":
            self.shift_mode = not self.shift_mode
            if self.shift_mode:
                self.caps_lock = False
            self._reload_key_values()
            return "shift"
        
        elif value == "space":
            self.text += " "
            return "space"
        
        # Regular character
        else:
            self.text += value
            # Auto-disable shift after typing a character
            if self.shift_mode and not self.caps_lock:
                self.shift_mode = False
                self._reload_key_values()
            return "char"
    
    def _reload_key_values(self):
        """Reload key values based on shift state"""
        for row in self.keys:
            for key in row:
                if not key.special:
                    key.value = self._get_key_value(key.label)
    
    def handle_dpad_command(self, command: str) -> dict:
        """
        Handle D-pad command and return state
        
        Args:
            command: "up", "down", "left", "right", "select"
        
        Returns:
            State dict with keyboard state
        """
        if command in ["up", "down", "left", "right"]:
            self.move_cursor(command)
        elif command in ["select", "ok"]:
            action = self.select_current_key()
            if action == "done":
                return {
                    "active": False,
                    "text": self.text,
                    "submitted": True,
                }
        
        return self.get_state()
    
    def get_state(self) -> dict:
        """Get current keyboard state for UI rendering"""
        current_key = self.get_current_key()
        
        return {
            "active": True,
            "text": self.text,
            "placeholder": self.placeholder,
            "cursor_row": self.cursor_row,
            "cursor_col": self.cursor_col,
            "current_key": current_key.label if current_key else None,
            "shift_mode": self.shift_mode,
            "caps_lock": self.caps_lock,
            "layout": [
                [
                    {
                        "label": key.label,
                        "value": key.value,
                        "row": key.row,
                        "col": key.col,
                        "width": key.width,
                        "special": key.special,
                        "selected": (key.row == self.cursor_row and key.col == self.cursor_col),
                    }
                    for key in row
                ]
                for row in self.keys
            ],
            "submitted": False,
        }


class KeyboardManager:
    """
    Manages on-screen keyboard instances per display/source
    """
    
    def __init__(self):
        self.keyboards: dict[str, OnScreenKeyboard] = {}
        self.active_keyboard: Optional[str] = None
    
    def show_keyboard(
        self,
        context_id: str,
        layout: KeyboardLayout = KeyboardLayout.QWERTY,
        initial_text: str = "",
        placeholder: str = "",
        on_submit: Optional[Callable[[str], None]] = None,
    ) -> OnScreenKeyboard:
        """
        Show keyboard for a specific context (e.g., "display-1:search")
        """
        keyboard = OnScreenKeyboard(
            layout=layout,
            initial_text=initial_text,
            placeholder=placeholder,
            on_submit=on_submit,
        )
        self.keyboards[context_id] = keyboard
        self.active_keyboard = context_id
        return keyboard
    
    def hide_keyboard(self, context_id: str):
        """Hide keyboard for a context"""
        if context_id in self.keyboards:
            del self.keyboards[context_id]
        if self.active_keyboard == context_id:
            self.active_keyboard = None
    
    def get_active_keyboard(self) -> Optional[OnScreenKeyboard]:
        """Get currently active keyboard"""
        if self.active_keyboard:
            return self.keyboards.get(self.active_keyboard)
        return None
    
    def handle_dpad_input(self, command: str) -> Optional[dict]:
        """
        Handle D-pad input for active keyboard
        Returns keyboard state or None if no active keyboard
        """
        keyboard = self.get_active_keyboard()
        if keyboard:
            return keyboard.handle_dpad_command(command)
        return None


# Frontend React component template
KEYBOARD_REACT_COMPONENT = """
// OnScreenKeyboard.tsx
import React from 'react';

interface Key {
  label: string;
  value: string;
  row: number;
  col: number;
  width: number;
  special: boolean;
  selected: boolean;
}

interface KeyboardState {
  active: boolean;
  text: string;
  placeholder: string;
  cursor_row: number;
  cursor_col: number;
  current_key: string | null;
  shift_mode: boolean;
  caps_lock: boolean;
  layout: Key[][];
  submitted: boolean;
}

interface Props {
  keyboardState: KeyboardState;
  onDpadCommand: (command: string) => void;
}

export const OnScreenKeyboard: React.FC<Props> = ({ keyboardState, onDpadCommand }) => {
  if (!keyboardState?.active) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg p-6 max-w-4xl w-full">
        {/* Text Input Display */}
        <div className="mb-6">
          <div className="bg-gray-800 rounded px-4 py-3 text-2xl text-white font-mono">
            {keyboardState.text || (
              <span className="text-gray-500">{keyboardState.placeholder}</span>
            )}
            <span className="animate-pulse">|</span>
          </div>
        </div>

        {/* Keyboard Grid */}
        <div className="space-y-2">
          {keyboardState.layout.map((row, rowIdx) => (
            <div key={rowIdx} className="flex justify-center gap-2">
              {row.map((key, colIdx) => (
                <button
                  key={`${rowIdx}-${colIdx}`}
                  className={`
                    px-4 py-3 rounded font-semibold text-lg
                    transition-all duration-150
                    ${key.width > 1 ? 'flex-grow' : 'w-16'}
                    ${key.selected 
                      ? 'bg-blue-600 text-white scale-110 shadow-lg' 
                      : 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                    }
                    ${key.special ? 'bg-gray-600' : ''}
                  `}
                  onClick={() => {
                    // Move cursor to this key
                    // Then select it
                  }}
                >
                  {key.label === '⌫' ? '←' : key.label === '✓' ? '✓ Done' : key.label}
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* Hint */}
        <div className="mt-4 text-center text-gray-400 text-sm">
          Use D-pad to navigate • Press OK to select • Select ✓ when done
        </div>
      </div>
    </div>
  );
};
"""
