"""
App runner state — instantiates the selected app and hands off control.

The app runs its own render loop on a background thread (managed by
BaseApp.start/stop). AppRunnerState polls app.is_done() each update cycle.

Transition back to menu when:
    - The app signals self._done = True from inside run()
    - The user presses the back button
"""

from .state import State


class AppRunnerState(State):
    """
    Instantiates ctx['selected_app'].app_class(hw) and runs it.
    Monitors app.is_done() and the back button. Returns to 'menu' when done.
    """

    EXIT_TO_MENU_CHIME = [(392, 0.1), (330, 0.1), (262, 0.1)]  # G4 → E4 → C4 falling arpeggio

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._next_state = None

        app_entry  = ctx.get('selected_app')
        if app_entry is None:
            print("[AppRunner] No app selected — returning to menu.")
            self._next_state = 'menu'
            self._app = None
            return

        print(f"[AppRunner] Starting: {app_entry.name}")
        self._app = app_entry.app_class(hw)
        self._app.start()

        # Back button is reserved for the runner, not the app
        hw.buttons['back'].on_press_callback = self._on_back

    def update(self) -> "str | None":
        if self._next_state is not None:
            return self._next_state

        if self._app is not None and self._app.is_done():
            print("[AppRunner] App finished — returning to menu.")
            self._stop_app()
            return 'menu'

        return None

    def exit(self) -> None:
        self._stop_app()
        self.hw.buttons['back'].on_press_callback = None

    def _on_back(self) -> None:
        print("[AppRunner] Back → menu.")
        self.hw.buzzer.play_sequence(self.EXIT_TO_MENU_CHIME)
        self._next_state = 'menu'

    def _stop_app(self) -> None:
        if self._app is not None:
            self._app.stop()
            self._app = None
