; Native 6502 emitted listing, NOT standalone MAC/65 master.
; Baseline r3 listing retained as r3_driver_reference.asm; exact patches below.
; Python builder is authoritative.
; State $2900; ZP $80..84,$86..89 reserved to this standalone executable.
; State STATE = $2900
; State LIVES = $2901
; State FIRE_ARM = $2902
; State TICK_OLD = $2903
; State DELTA = $2904
; State UNITS = $2905
; State TIME0 = $2906
; State TIME1 = $2907
; State DIST0 = $2908
; State DIST1 = $2909
; State DIST2 = $290A
; State WARN = $290B
; State FLASH = $290C
; State FLASH_TIME = $290D
; State EXP_TIME = $290E
; State EXP_PHASE = $290F
; State TMP = $2910
; State TMP2 = $2911
; State MUL0 = $2912
; State MUL1 = $2913
; State MUL2 = $2914
; State RATE0 = $2915
; State RATE1 = $2916
; State RATE2 = $2917
; State NUM0 = $2918
; State NUM1 = $2919
; State NUM2 = $291A
; State REM0 = $291B
; State REM1 = $291C
; State DEN0 = $291D
; State DEN1 = $291E
; State PERCENT = $291F
; State CENTIMILES = $2920
; State MPH = $2921
; State HUND = $2922
; State TENS = $2923
; State ONES = $2924
; State LAST_GAS = $2925
; State LAST_MI = $2926
; State LAST_MPH = $2927
; State LAST_LIVES = $2928
; State LAST_FLASH = $2929
; State SHAKE_TIME = $292A
; Driver patches: [{"address": 8443, "jump": 28672, "purpose": "RESET"}, {"address": 8510, "jump": 28874, "purpose": "FRAME"}, {"address": 8764, "jump": 29195, "purpose": "TELEMETRY"}, {"address": 8604, "bytes": "e584", "purpose": "warning steering step from private ZP $84"}, {"address": 8638, "bytes": "6584", "purpose": "warning steering step from private ZP $84"}]
    *= $7000
NEW_GAME:
    LDA #$03
    STA $2901
ATTEMPT:
    LDA #$00
    STA $2900
    STA $2902
    STA $2906
    STA $2907
    STA $290B
    STA $290D
    STA $290E
    STA $290F
    STA $292A
    LDA #$00
    STA $2908
    LDA #$D6
    STA $2909
    LDA #$83
    STA $290A
    LDA #$01
    STA $290C
    LDA #$05
    STA $2905
    LDA $0062
    BEQ NTSC
    LDA #$06
    STA $2905
NTSC:
    LDA $0014
    STA $2903
    LDA #$0C
    STA $84
    LDA #$FF
    STA $2925
    STA $2926
    STA $2927
    STA $2928
    STA $2929
    LDX #$00
RESTORE_PMG:
    LDA $9800,X
    STA $3800,X
    LDA $9900,X
    STA $3900,X
    LDA $9A00,X
    STA $3A00,X
    LDA $9B00,X
    STA $3B00,X
    LDA $9C00,X
    STA $3C00,X
    LDA $9D00,X
    STA $3D00,X
    LDA $9E00,X
    STA $3E00,X
    LDA $9F00,X
    STA $3F00,X
    INX
    BNE RESTORE_PMG
    LDA #$02
    STA $D01D
    LDA #$36
    STA $02C0
    LDA #$36
    STA $D012
    LDA #$0E
    STA $02C1
    LDA #$0E
    STA $D013
    LDA #$B0
    STA $23A5
    LDA #$00
    STA $86
    LDA #$94
    STA $87
    JSR BLIT
    LDA #$00
    STA $2394
    JSR $2100
    JSR HUD
    RTS
FRAME:
    LDA $0014
    SEC
    SBC $2903
    STA $2904
    LDA $0014
    STA $2903
    LDA $2904
    BNE HAS_TICK
    RTS
HAS_TICK:
    LDA #$00
    STA $2911
    LDA $2904
    STA $2910
    ASL A
    ROL $2911
    STA $2912
    LDA $2911
    STA $2913
    LDA $2905
    CMP #$06
    BEQ PAL_STEP
    LDA $2912
    ASL $2912
    ROL $2913
    LDA $2912
    CLC
    ADC $2904
    STA $2912
    LDA $2913
    ADC #$00
    STA $2913
    JMP STEP_READY
PAL_STEP:
    LDA $2912
    STA $2910
    LDA $2913
    STA $2911
    ASL $2912
    ROL $2913
    LDA $2912
    CLC
    ADC $2910
    STA $2912
    LDA $2913
    ADC $2911
    STA $2913
STEP_READY:
    JSR FIRE_EDGE
    LDA $2900
    BEQ DRIVING
    CMP #$01
    BNE RESULT_INPUT
    JMP EXPLOSION_TICK
RESULT_INPUT:
    LDA $2911
    BNE RESULT_PRESS
    RTS
RESULT_PRESS:
    LDA #$00
    STA $2902
    LDA $2900
    CMP #$02
    BNE NOT_RETRY
    JMP ATTEMPT
NOT_RETRY:
    CMP #$04
    BNE RESULT_NEW
    LDA #$05
    STA $2900
    LDA #$00
    STA $86
    LDA #$84
    STA $87
    JSR BLIT
    JSR HUD_DIRTY
    RTS
RESULT_NEW:
    JMP NEW_GAME
DRIVING:
    LDA $2390
    STA $02F4
    STA $D409
    LDA $2392
    STA $2393
    JSR $2162
    LDA $2906
    CLC
    ADC $2912
    STA $2906
    LDA $2907
    ADC $2913
    STA $2907
    JSR DISTANCE
    LDA $2906
    CMP #$5C
    LDA $2907
    SBC #$C1
    BCC NOT_DEADLINE
    JMP FAIL_BEGIN
NOT_DEADLINE:
    LDA $2908
    ORA $2909
    ORA $290A
    BNE KEEP_DRIVING
    LDA #$04
    STA $2900
    LDA #$00
    STA $2902
    LDA #$01
    STA $290C
    LDA #$00
    STA $D01D
    LDA #$00
    STA $86
    LDA #$80
    STA $87
    JSR BLIT
    JSR HUD_DIRTY
    RTS
KEEP_DRIVING:
    JSR WARNINGS
    JSR HUD
    RTS
FIRE_EDGE:
    LDA #$00
    STA $2911
    LDA $D010
    AND #$01
    BEQ PRESSED
    LDA #$01
    STA $2902
    RTS
PRESSED:
    LDA $2902
    STA $2911
    LDA #$00
    STA $2902
    RTS
TELEMETRY:
    JSR $22C3
    LDA $2397
    STA $239B
    LDA $2398
    STA $239C
    LSR $239C
    ROR $239B
    LSR $239C
    ROR $239B
    LSR $239C
    ROR $239B
    LSR $239C
    ROR $239B
    LDA $239B
    CLC
    ADC #$30
    STA $D000
    STA $D001
    RTS
DISTANCE:
    LDX $2396
    LDA $2905
    CMP #$06
    BEQ PAL_RATE
    LDA $6900,X
    STA $2915
    LDA $6A00,X
    JMP RATE_READY
PAL_RATE:
    LDA $6B00,X
    STA $2915
    LDA $6C00,X
RATE_READY:
    STA $2916
    LDA #$00
    STA $2917
    STA $2918
    STA $2919
    STA $291A
    LDA $2904
    STA $2910
    LDX #$08
MULTIPLY:
    LSR $2910
    BCC NO_ADD
    CLC
    LDA $2918
    ADC $2915
    STA $2918
    LDA $2919
    ADC $2916
    STA $2919
    LDA $291A
    ADC $2917
    STA $291A
NO_ADD:
    ASL $2915
    ROL $2916
    ROL $2917
    DEX
    BNE MULTIPLY
    SEC
    LDA $2908
    SBC $2918
    STA $2908
    LDA $2909
    SBC $2919
    STA $2909
    LDA $290A
    SBC $291A
    STA $290A
    BCS DIST_OK
    LDA #$00
    STA $2908
    STA $2909
    STA $290A
DIST_OK:
    RTS
WARNINGS:
    LDA #$00
    STA $2910
    LDA $2906
    CMP #$05
    LDA $2907
    SBC #$91
    BCC W75
    LDA #$01
    STA $2910
W75:
    LDA $2906
    CMP #$06
    LDA $2907
    SBC #$AE
    BCC W90
    LDA #$02
    STA $2910
W90:
    LDA $2910
    CMP $290B
    BEQ SAME_WARN
    STA $290B
    LDA #$00
    STA $290D
    LDA #$01
    STA $290C
SAME_WARN:
    LDX $290B
    LDA $6E00,X
    STA $84
    LDA $290B
    BNE DO_FLASH
    RTS
DO_FLASH:
    LDA $290D
    CLC
    ADC $2912
    STA $290D
    LDA $2913
    ADC #$00
    STA $2911
    LDX $290B
    LDA $6E03,X
    STA $2910
FLASH_REDUCE:
    LDA $2911
    BNE FLASH_SUB
    LDA $290D
    CMP $2910
    BCC NO_FLASH
FLASH_SUB:
    LDA $290D
    SEC
    SBC $2910
    STA $290D
    LDA $2911
    SBC #$00
    STA $2911
    LDA $290C
    EOR #$01
    STA $290C
    JMP FLASH_REDUCE
NO_FLASH:
    INC $292A
    LDA $292A
    AND #$04
    BEQ SHAKE_LEFT
    LDA $D000
    CLC
    ADC $290B
    CMP #$95
    BCC SHAKE_SET
    LDA #$94
    JMP SHAKE_SET
SHAKE_LEFT:
    LDA $D000
    SEC
    SBC $290B
    CMP #$30
    BCS SHAKE_SET
    LDA #$30
SHAKE_SET:
    STA $D000
    STA $D001
    RTS
FAIL_BEGIN:
    LDA #$5C
    STA $2906
    LDA #$C1
    STA $2907
    LDA #$01
    STA $2900
    STA $290C
    LDA #$00
    STA $2902
    STA $290E
    STA $290F
    JSR EXP_DRAW
    JSR HUD
    RTS
EXPLOSION_TICK:
    LDA $290E
    CLC
    ADC $2912
    BCS EXP_DONE
    STA $290E
    LDA $2913
    BNE EXP_DONE
    LDA $290E
    CMP #$96
    BCS EXP_DONE
    CMP #$64
    BCC EXP_UNDER100
    LDA #$02
    JMP EXP_PHASE_READY
EXP_UNDER100:
    CMP #$32
    BCC EXP_WAIT
    LDA #$01
EXP_PHASE_READY:
    CMP $290F
    BEQ EXP_WAIT
    STA $290F
    JSR EXP_DRAW
EXP_WAIT:
    RTS
EXP_DONE:
    LDA $2901
    BEQ NO_LIVES
    DEC $2901
NO_LIVES:
    LDA #$00
    STA $2902
    LDA #$00
    STA $D01D
    LDA $2901
    BEQ GAME_OVER
    LDA #$02
    STA $2900
    LDA #$00
    STA $86
    LDA #$88
    STA $87
    JSR BLIT
    JMP END_FAIL
GAME_OVER:
    LDA #$03
    STA $2900
    LDA #$00
    STA $86
    LDA #$8C
    STA $87
    JSR BLIT
END_FAIL:
    JSR HUD_DIRTY
    RTS
EXP_DRAW:
    LDX #$00
    LDA #$00
EXP_CLEAR:
    STA $3C00,X
    STA $3D00,X
    INX
    BNE EXP_CLEAR
    LDA #$C8
    STA $02C0
    LDA #$C8
    STA $D012
    LDA #$C8
    STA $02C1
    LDA #$C8
    STA $D013
    LDA $290F
    ASL A
    ASL A
    ASL A
    STA $2910
    ASL A
    CLC
    ADC $2910
    TAY
    LDA $23A5
    SEC
    SBC #$04
    TAX
    LDA #$18
    STA $2910
EXP_ROWS:
    LDA $6E10,Y
    STA $3C00,X
    STA $3D00,X
    INX
    INY
    DEC $2910
    BNE EXP_ROWS
    RTS
DIVIDE:
    LDA #$00
    STA $291B
    STA $291C
    LDX #$18
DIV_BIT:
    ASL $2918
    ROL $2919
    ROL $291A
    ROL $291B
    ROL $291C
    BCS DIV_SUB
    LDA $291B
    CMP $291D
    LDA $291C
    SBC $291E
    BCC DIV_NEXT
DIV_SUB:
    SEC
    LDA $291B
    SBC $291D
    STA $291B
    LDA $291C
    SBC $291E
    STA $291C
    INC $2918
DIV_NEXT:
    DEX
    BNE DIV_BIT
    RTS
DIGITS:
    STA $2910
    LDA #$00
    STA $2922
    STA $2923
    LDA $2910
DIG100:
    CMP #$64
    BCC DIG10
    SEC
    SBC #$64
    INC $2922
    JMP DIG100
DIG10:
    CMP #$0A
    BCC DIG_END
    SEC
    SBC #$0A
    INC $2923
    JMP DIG10
DIG_END:
    CLC
    ADC #$D0
    STA $2924
    LDA $2922
    CLC
    ADC #$D0
    STA $2922
    LDA $2923
    CLC
    ADC #$D0
    STA $2923
    RTS
HUD_DIRTY:
    LDA #$FF
    STA $2925
    STA $2926
    STA $2927
    STA $2928
    STA $2929
HUD:
    LDA $2906
    STA $2918
    LDA $2907
    STA $2919
    LDA #$00
    STA $291A
    LDA #$EF
    STA $291D
    LDA #$01
    STA $291E
    JSR DIVIDE
    LDA $2918
    STA $291F
    LDA $2908
    STA $2918
    LDA $2909
    STA $2919
    LDA $290A
    STA $291A
    LDA #$C0
    STA $291D
    LDA #$A8
    STA $291E
    JSR DIVIDE
    LDA $291B
    ORA $291C
    BEQ MI_EXACT
    INC $2918
MI_EXACT:
    LDA $2918
    STA $2920
    CMP $2926
    BEQ MI_UNCHANGED
    STA $2926
    JSR DIGITS
    LDA $2922
    STA $255E
    LDA $2923
    STA $2560
    LDA $2924
    STA $2561
MI_UNCHANGED:
    LDX $2396
    LDA $6D00,X
    STA $2921
    CMP $2927
    BEQ MPH_UNCHANGED
    STA $2927
    JSR DIGITS
    JSR LEADING
    LDA $2922
    STA $25FE
    LDA $2923
    STA $25FF
    LDA $2924
    STA $2600
MPH_UNCHANGED:
    LDA $2901
    CMP $2928
    BEQ LIVES_UNCHANGED
    STA $2928
    LDA $2901
    CMP #$01
    LDA #$C0
    BCC LIFE0
    LDA #$A0
LIFE0:
    STA $269E
    LDA $2901
    CMP #$02
    LDA #$C0
    BCC LIFE1
    LDA #$A0
LIFE1:
    STA $26A1
    LDA $2901
    CMP #$03
    LDA #$C0
    BCC LIFE2
    LDA #$A0
LIFE2:
    STA $26A4
LIVES_UNCHANGED:
    LDA $291F
    CMP $2925
    BNE GAS_CHANGED
    LDA $290C
    CMP $2929
    BNE GAS_CHANGED
    RTS
GAS_CHANGED:
    LDA $291F
    STA $2925
    LDA $290C
    STA $2929
    LDA $291F
    JSR DIGITS
    JSR LEADING
    LDA $290C
    BNE GAS_VISIBLE
    LDA #$C0
    STA $2922
    STA $2923
    STA $2924
GAS_VISIBLE:
    LDA $2922
    STA $24BE
    LDA $2923
    STA $24BF
    LDA $2924
    STA $24C0
    LDA $290C
    BEQ PERCENT_HIDDEN
    LDA #$C5
    JMP PERCENT_SET
PERCENT_HIDDEN:
    LDA #$C0
PERCENT_SET:
    STA $24C1
    LDA $291F
    LDA #$00
    STA $2910
    LDA $291F
BAR_COUNT:
    CMP #$01
    BCC BAR_READY
    INC $2910
    SEC
    SBC #$0A
    BCS BAR_COUNT
BAR_READY:
    LDX #$00
BAR_LOOP:
    LDA $290C
    BEQ BAR_BLANK
    TXA
    CMP $2910
    LDA #$A2
    BCS BAR_STORE
    LDA #$A1
    JMP BAR_STORE
BAR_BLANK:
    LDA #$C0
BAR_STORE:
    STA $246C,X
    INX
    CPX #$0A
    BCC BAR_LOOP
    RTS
LEADING:
    LDA $2922
    CMP #$D0
    BNE LEAD_DONE
    LDA #$C0
    STA $2922
    LDA $2923
    CMP #$D0
    BNE LEAD_DONE
    LDA #$C0
    STA $2923
LEAD_DONE:
    RTS
BLIT:
    LDA #$00
    STA $88
    LDA #$24
    STA $89
    LDX #$03
    LDY #$00
BLIT_PAGE:
    LDA ($86),Y
    STA ($88),Y
    INY
    BNE BLIT_PAGE
    INC $87
    INC $89
    DEX
    BNE BLIT_PAGE
BLIT_TAIL:
    LDA ($86),Y
    STA ($88),Y
    INY
    CPY #$C0
    BCC BLIT_TAIL
    RTS
