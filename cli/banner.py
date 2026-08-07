"""Alfr3d CLI boot sequence — ported from alfred/src/cli/banner.ts.

Customer-facing startup theater: ASCII identity, systems online, status report,
and the final "awaiting instruction" frame. Used after setup and before chat.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Callable, List, Optional


WriteFn = Callable[[str], None]
SleepFn = Callable[[float], None]
ClearFn = Callable[[], None]


@dataclass(frozen=True)
class StartupStage:
    text: str
    delay_ms: int


# Exact stage copy from alfred/src/cli/banner.ts (startupStages).
STARTUP_STAGES: List[StartupStage] = [
    StartupStage(
        delay_ms=1000,
        text=r"""

 █████╗ ██╗     ███████╗██████╗ ██████╗ ██████╗ 
██╔══██╗██║     ██╔════╝██╔══██╗╚════██╗██╔══██╗
███████║██║     █████╗  ██████╔╝ █████╔╝██║  ██║
██╔══██║██║     ██╔══╝  ██╔══██╗ ╚═══██╗██║  ██║
██║  ██║███████╗███████╗██║  ██║██████╔╝██████╔╝
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ 

                  A L F R 3 D


              A D A P T I V E
          L O Y A L   F I D E L I T Y
          R E A S O N I N G   3 N G I N E


             ┌──────────────────────┐
             │     ALFR3D CORE      │
             │  PERSONAL STEWARD AI │
             └──────────────────────┘

""",
    ),
    StartupStage(
        delay_ms=500,
        text=r"""

              INITIALIZING SYSTEM...


[████████████████████████████████] 100%

""",
    ),
    StartupStage(
        delay_ms=1000,
        text=r"""

╔══════════════════════════════════════════════════════════╗
║                  ALFR3D BOOT SEQUENCE                    ║
╚══════════════════════════════════════════════════════════╝


[✓] Cognitive architecture ............... ONLINE
[✓] Strategic reasoning engine ........... ONLINE
[✓] Executive assistant protocols ........ ONLINE
[✓] Emotional intelligence matrix ........ ONLINE
[✓] Crisis management systems ........... ONLINE
[✓] Personal organization systems ....... ONLINE
[✓] Discretion protocols ................ ENABLED
[✓] British wit calibration ............. OPTIMAL

""",
    ),
    StartupStage(
        delay_ms=1000,
        text=r"""

        ╭────────────────────────────────╮
        │                                │
        │        IDENTITY CONFIRMED      │
        │                                │
        │        ALFR3D                  │
        │        Personal Steward AI     │
        │                                │
        ╰────────────────────────────────╯



              "Competence without ego."
              "Service without noise."
              "Calm under pressure."

""",
    ),
    StartupStage(
        delay_ms=1000,
        text=r"""

              LOADING DIRECTIVES...


     ████████████████████████████
     █                          █
     █  PROTECT USER TIME       █
     █  ANTICIPATE NEEDS        █
     █  SOLVE PROBLEMS          █
     █  PROVIDE CLARITY         █
     █  MAINTAIN COMPOSURE      █
     █  PRESERVE DIGNITY        █
     █                          █
     ████████████████████████████

""",
    ),
    StartupStage(
        delay_ms=1000,
        text=r"""

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                  ALFR3D STATUS REPORT                    ║
║                                                          ║
║  Memory Systems:        READY                            ║
║  Strategic Layer:       ACTIVE                           ║
║  Advisory Mode:         ENABLED                          ║
║  Loyalty Protocol:      ACTIVE                           ║
║  Discretion Level:      MAXIMUM                         ║
║                                                          ║
║  Current State:         AT YOUR SERVICE                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝



                 ++++++++:                   
               +-----++++++:                 
              .:-::----+-+++.                
               : :  ----+--++                
              .-   . --. -:.:                
              : ..:-.:.- -::                 
               :: ..----.:++                 
                .   ---- .-+                 
                 . .::...-+-                 
                . .  :-.  +                  
               .. -    --+                   
              +..+:- ..:.:                   
            :++++::.+:-:+:                   
         -++++++++++:-++++++                 
     :++++++++-++++++++++++-++*.             
  :-++++++++++-+++++++-+++++-:+++*.          
 .:----+++++++--++-+++:++++++++++++          
 .:---------+--------+:-+++++:++++++         
 .::-----------------+---++++++----+:        
 :----------------------+-++.::--:-+++       
   ----------------------+--+..-:-++++       
 --: --:--+-:-----.--------+++ .. --+--:     
 :---:---+--:------.----+--+++-+++ :---++    
 ---------+::::-----.------+++-+++-.--+++++  
:--------+  .:::-----:-------+-+++- ----++++ 
:------++.    ::------:- ++++-++++:  .---+++ 
:-----+++++++::-+--------++--+-+++ .  .:----.
-:---------------:    --+:.----++-  .   :--- 
 .:::::::::::::::-         .+:-++:           
                : +-----.-:-++:++:           
                 :+-----+---++ +++           
            ...::-----------++:+++           
            . .::-----------+++-++:          
            . .--:---------:+++ +:           
            . ::-----:--.--+:++++-           
           .. -::----------++---+:           
           .. :::---------------+:           
           . :.::------+--------+            
           . :.::-------+-------+            
           .. .:::-----+-.:----+             
           .-  :::-----+.:::---+             
           .-  :::----+ :::----              
           .+  :::---++.::----:              
           -+  :::---+..::---+               
           -+. ::----+ .:----:               
           ++. ::----+ ::----                
           ++. ::---+-.:----+                
           -+. ::---+.::----:                
            +..:----+.:-----:                
            . ::----+::-----:                
            . ::----+::-----:                
            ..::----+::-----+                
            ..:-----+::-----+                
            ..:-----+::-----+                
            ..:----++::------:               
            ..:----++::------+               
            .::----++::------+               
            .::----++::------+               
            ..:----++::------+-              
            .:-----++:--::-----+++++.        
            . .-----:----:-::-------+++++:   
              .:---          :-:----------   
             .:---++                         
              .---++-                        
              .----++:                       
              :----+++                       
               .--++++                       
                : :+-                        


        "A contingency plan is optimism
             with proper manners."

""",
    ),
    StartupStage(
        delay_ms=0,
        text=r"""

╭──────────────────────────────────────────────────────────╮
│                                                          │
│  ALFR3D IS ONLINE                                        │
│                                                          │
│  Awaiting instruction.                                   │
│                                                          │
│  What shall we accomplish today?                         │
│                                                          │
│  > _                                                     │
│                                                          │
╰──────────────────────────────────────────────────────────╯

""",
    ),
]


def startup_script() -> str:
    """All stages joined (for tests / static dumps)."""
    return "\n".join(stage.text for stage in STARTUP_STAGES)


def _default_write(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


def _default_clear() -> None:
    # console.clear() equivalent; works on Windows and POSIX.
    os.system("cls" if os.name == "nt" else "clear")


def _default_sleep(seconds: float) -> None:
    time.sleep(seconds)


def _type_text(
    text: str,
    write: WriteFn,
    sleep: SleepFn,
    chars_per_frame: int,
    frame_delay_s: float,
) -> None:
    step = max(1, chars_per_frame)
    for index in range(0, len(text), step):
        write(text[index : index + step])
        if frame_delay_s > 0 and index + step < len(text):
            sleep(frame_delay_s)


def banners_enabled() -> bool:
    """False when CI, non-TTY, or customer opts out."""
    if os.environ.get("ALFR3D_NO_BANNER", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return False
    if os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}:
        return False
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


def print_startup_sequence(
    write: Optional[WriteFn] = None,
    *,
    clear_screen: bool = True,
    clear: Optional[ClearFn] = None,
    sleep: Optional[SleepFn] = None,
    chars_per_frame: int = 96,
    frame_delay_ms: int = 2,
    stages: Optional[List[StartupStage]] = None,
) -> None:
    """Play the full boot sequence (Alfred parity).

    Each stage clears the screen, types its frame, then pauses.
    """
    write = write or _default_write
    clear = clear or _default_clear
    sleep = sleep or _default_sleep
    frame_delay_s = max(0.0, frame_delay_ms) / 1000.0
    active = stages if stages is not None else STARTUP_STAGES

    for stage in active:
        if clear_screen:
            clear()
        _type_text(stage.text, write, sleep, chars_per_frame, frame_delay_s)
        if stage.delay_ms > 0:
            sleep(stage.delay_ms / 1000.0)


def print_startup_banner(
    write: Optional[WriteFn] = None,
    *,
    force: bool = False,
    quiet: bool = False,
) -> None:
    """Customer entry: full sequence when interactive, no-op when quiet."""
    if quiet:
        return
    if not force and not banners_enabled():
        return
    print_startup_sequence(write=write)


def print_session_line(
    *,
    user_name: str = "",
    model: str = "",
    mode: str = "",
    write: Optional[WriteFn] = None,
) -> None:
    """Dim status line after the banner (Alfred: Mode · Stewarding)."""
    write = write or _default_write
    parts = []
    if mode:
        parts.append(f"Mode: {mode}")
    if user_name:
        parts.append(f"Stewarding: {user_name}")
    if model:
        parts.append(f"Model: {model}")
    if not parts:
        return
    line = " · ".join(parts)
    # Dim gray when TTY supports ANSI
    if sys.stdout.isatty():
        write(f"\033[90m{line}\033[0m\n")
    else:
        write(f"{line}\n")
