; Authoritative emitter: tools/build_stage1_v04.py
    *= $0400
NEW_INIT:
    LDA #$00
    STA $D40E
    JSR $1189
    JSR ALIGN
    LDA $14
    STA MOTION_CLOCK
    LDA #$00
    STA OLD_Y
    LDX #$00
CLEAR_PMG:
    STA $B800
    STA $B900
    STA $BA00
    STA $BB00
    STA $BC00
    STA $BD00
    STA $BE00
    STA $BF00
    INX
    branch CLEAR_PMG
    LDA #$B8
    STA $D407
    LDA #$00
    STA $D008
    LDA #$00
    STA $D009
    LDA #$00
    STA $D00A
    LDA #$00
    STA $D00B
    LDA #$02
    STA $D01D
    LDA #$01
    STA $026F
    LDA #$01
    STA $D01B
    LDA #$36
    STA $02C0
    LDA #$36
    STA $D012
    LDA #$3A
    STA $022F
    LDA #$3A
    STA $D400
    JSR PMG_DRAW
    RTS
ALIGN:
    LDA C_PX
    LSR A
    STA POS_XH
    LDA #$00
    ROR A
    STA POS_X
    LDA C_PY
    LSR A
    STA POS_YH
    LDA #$00
    ROR A
    STA POS_Y
    RTS
GLYPH_DISPATCH:
    LDA C_GLYPH
    CMP #$0E
    branch CORE_GLYPH
    RTS
CORE_GLYPH:
    LDA C_NY
    JMP $1D7A
MOVE:
    LDA $14
    SEC
    SBC MOTION_CLOCK
    branch NEW_TICK
    RTS
NEW_TICK:
    CMP #$03
    branch DELTA_OK
    LDA #$02
DELTA_OK:
    STA UPDATES
    LDA $14
    STA MOTION_CLOCK
    LDA #$00
    STA C_SEP_0
    STA C_SEP_1
    STA C_SEP_2
    LDA $D300
    STA JOY
    LDA #$00
    STA SIGN_X
    STA SIGN_Y
    LDA JOY
    AND #$0C
    CMP #$08
    branch POSITIVE_X
    LDA #$FF
    STA SIGN_X
    JMP INPUT_DONE_X
POSITIVE_X:
    CMP #$04
    branch INPUT_DONE_X
    LDA #$01
    STA SIGN_X
INPUT_DONE_X:
    LDA JOY
    AND #$03
    CMP #$02
    branch POSITIVE_Y
    LDA #$FF
    STA SIGN_Y
    JMP INPUT_DONE_Y
POSITIVE_Y:
    CMP #$01
    branch INPUT_DONE_Y
    LDA #$01
    STA SIGN_Y
INPUT_DONE_Y:
UPDATE:
    LDA #$18
    STA SPEED
    LDA #$00
    STA DIAGONAL
    LDA SIGN_X
    branch SPEED_READY
    LDA SIGN_Y
    branch SPEED_READY
    LDA #$11
    STA SPEED
    LDA #$01
    STA DIAGONAL
SPEED_READY:
    LDA #$00
    STA AXIS
    LDA SIGN_X
    STA SIGN
    LDA SPEED
    STA REMAIN
    JSR AXIS_MOVE
    LDA BLOCKED
    STA BLOCK_X
    LDA #$02
    STA AXIS
    LDA SIGN_Y
    STA SIGN
    LDA SPEED
    STA REMAIN
    LDA BLOCK_X
    branch Y_SPEED
    LDA #$18
    STA REMAIN
Y_SPEED:
    JSR AXIS_MOVE
    LDA BLOCKED
    branch MOTION_DONE
    LDA BLOCK_X
    branch MOTION_DONE
    LDA DIAGONAL
    branch MOTION_DONE
    LDA #$00
    STA AXIS
    LDA SIGN_X
    STA SIGN
    LDA #$07
    STA REMAIN
    JSR AXIS_MOVE
MOTION_DONE:
    LDA POS_X
    CLC
    ADC #$40
    STA TMP_LO
    LDA POS_XH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA C_PX
    LDA POS_Y
    CLC
    ADC #$40
    STA TMP_LO
    LDA POS_YH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA C_PY
    LDA C_ROOM
    STA OLD_ROOM
    STA C_LOOK_ROOM
    LDA C_PX
    STA C_NX
    LDA C_PY
    STA C_NY
    JSR C_TRY_MOVE
    LDA C_ROOM
    CMP OLD_ROOM
    branch NO_ROOM_CHANGE
    JSR ALIGN
    JMP MOVE_FINISH
NO_ROOM_CHANGE:
    LDA C_ROOM
    CMP #$02
    branch MORE_UPDATES
    LDA C_PX
    CMP #$27
    branch MORE_UPDATES
    LDA C_PY
    CMP #$0A
    branch MORE_UPDATES
    LDA #$02
    STA C_STATE
    JMP MOVE_FINISH
MORE_UPDATES:
    DEC UPDATES
    branch MOVE_FINISH
    JMP UPDATE
MOVE_FINISH:
    JSR PMG_DRAW
    RTS
AXIS_MOVE:
    LDA #$00
    STA BLOCKED
    LDA SIGN
    branch AXIS_LOOP
    RTS
AXIS_LOOP:
    LDA REMAIN
    CMP #$11
    branch CHUNK_READY
    LDA #$10
CHUNK_READY:
    STA CHUNK
    STA AMOUNT
    LDX AXIS
    LDA POS_X,X
    STA SAVE_LO
    LDA POS_XH,X
    STA SAVE_HI
    JSR APPLY
    JSR BOX_OK
    branch AXIS_COLLISION
    LDA REMAIN
    SEC
    SBC CHUNK
    STA REMAIN
    branch AXIS_LOOP
    RTS
AXIS_COLLISION:
    LDA #$01
    STA BLOCKED
    LDA #$00
    STA LOW
    LDA CHUNK
    CLC
    ADC #$FF
    STA HIGH
BINARY:
    LDA LOW
    CMP HIGH
    branch BINARY_DONE
    CLC
    ADC HIGH
    CLC
    ADC #$01
    LSR A
    STA MID
    STA AMOUNT
    JSR APPLY
    JSR BOX_OK
    branch BINARY_BAD
    LDA MID
    STA LOW
    JMP BINARY
BINARY_BAD:
    LDA MID
    CLC
    ADC #$FF
    STA HIGH
    JMP BINARY
BINARY_DONE:
    LDA LOW
    STA AMOUNT
    JSR APPLY
    RTS
APPLY:
    LDX AXIS
    LDA SIGN
    CMP #$01
    branch APPLY_MINUS
    LDA SAVE_LO
    CLC
    ADC AMOUNT
    STA POS_X,X
    LDA SAVE_HI
    ADC #$00
    STA POS_XH,X
    RTS
APPLY_MINUS:
    LDA SAVE_LO
    SEC
    SBC AMOUNT
    STA POS_X,X
    LDA SAVE_HI
    SBC #$00
    STA POS_XH,X
    RTS
BOX_OK:
    LDA POS_XH
    CMP #$14
    branch inverse LONG_707
    JMP BOX_BAD
LONG_707:
    CMP #$13
    branch BOUNDS_X
    LDA POS_X
    CMP #$81
    branch inverse LONG_721
    JMP BOX_BAD
LONG_721:
BOUNDS_X:
    LDA POS_YH
    CMP #$0B
    branch inverse LONG_731
    JMP BOX_BAD
LONG_731:
    CMP #$0A
    branch BOUNDS_Y
    LDA POS_Y
    CMP #$81
    branch inverse LONG_745
    JMP BOX_BAD
LONG_745:
BOUNDS_Y:
    LDA POS_X
    CLC
    ADC #$10
    STA TMP_LO
    LDA POS_XH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA LEFT
    LDA POS_X
    CLC
    ADC #$6F
    STA TMP_LO
    LDA POS_XH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA RIGHT
    LDA POS_Y
    CLC
    ADC #$10
    STA TMP_LO
    LDA POS_YH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA TOP
    LDA POS_Y
    CLC
    ADC #$6F
    STA TMP_LO
    LDA POS_YH
    ADC #$00
    STA TMP_HI
    LDA TMP_LO
    CMP #$80
    LDA TMP_HI
    ROL A
    STA BOTTOM
    LDA C_ROOM
    STA C_LOOK_ROOM
    LDA LEFT
    STA C_NX
    LDA TOP
    STA C_NY
    JSR C_WALK
    branch inverse LONG_887
    JMP BOX_BAD
LONG_887:
    LDA RIGHT
    CMP LEFT
    branch SKIP_TOP_RIGHT
    STA C_NX
    JSR C_WALK
    branch inverse LONG_906
    JMP BOX_BAD
LONG_906:
SKIP_TOP_RIGHT:
    LDA BOTTOM
    CMP TOP
    branch BOX_GOOD
    STA C_NY
    LDA LEFT
    STA C_NX
    JSR C_WALK
    branch inverse LONG_931
    JMP BOX_BAD
LONG_931:
    LDA RIGHT
    CMP LEFT
    branch BOX_GOOD
    STA C_NX
    JSR C_WALK
    branch inverse LONG_950
    JMP BOX_BAD
LONG_950:
BOX_GOOD:
    LDA #$01
    RTS
BOX_BAD:
    LDA #$00
    RTS
CONTACT:
    LDA #$00
    STA CONTACT_ID
CONTACT_LOOP:
    LDX CONTACT_ID
    LDA C_E_ACTIVE,X
    branch inverse LONG_972
    JMP CONTACT_NEXT
LONG_972:
    LDA C_E_STUN,X
    branch inverse LONG_980
    JMP CONTACT_NEXT
LONG_980:
    LDA C_E_SEPARATE,X
    branch inverse LONG_988
    JMP CONTACT_NEXT
LONG_988:
    LDA C_E_ENTRY_GRACE,X
    branch inverse LONG_996
    JMP CONTACT_NEXT
LONG_996:
    LDA C_E_EROOM,X
    CMP C_ROOM
    branch inverse LONG_1007
    JMP CONTACT_NEXT
LONG_1007:
    LDX CONTACT_ID
    LDA C_E_EX,X
    LSR A
    STA ENEMY_HI
    LDA #$00
    ROR A
    STA ENEMY_LO
    LDA POS_X
    SEC
    SBC ENEMY_LO
    STA DIFF_LO
    LDA POS_XH
    SBC ENEMY_HI
    STA DIFF_HI
    branch DIFF_POS_X
    LDA DIFF_LO
    EOR #$FF
    CLC
    ADC #$01
    STA DIFF_LO
    LDA DIFF_HI
    EOR #$FF
    ADC #$00
    STA DIFF_HI
DIFF_POS_X:
    LDA DIFF_HI
    branch inverse LONG_1073
    JMP CONTACT_NEXT
LONG_1073:
    LDA DIFF_LO
    CMP #$60
    branch inverse LONG_1083
    JMP CONTACT_NEXT
LONG_1083:
    LDX CONTACT_ID
    LDA C_E_EY,X
    LSR A
    STA ENEMY_HI
    LDA #$00
    ROR A
    STA ENEMY_LO
    LDA POS_Y
    SEC
    SBC ENEMY_LO
    STA DIFF_LO
    LDA POS_YH
    SBC ENEMY_HI
    STA DIFF_HI
    branch DIFF_POS_Y
    LDA DIFF_LO
    EOR #$FF
    CLC
    ADC #$01
    STA DIFF_LO
    LDA DIFF_HI
    EOR #$FF
    ADC #$00
    STA DIFF_HI
DIFF_POS_Y:
    LDA DIFF_HI
    branch inverse LONG_1149
    JMP CONTACT_NEXT
LONG_1149:
    LDA DIFF_LO
    CMP #$60
    branch inverse LONG_1159
    JMP CONTACT_NEXT
LONG_1159:
    LDA #$01
    STA C_STATE
    RTS
CONTACT_NEXT:
    INC CONTACT_ID
    LDA CONTACT_ID
    CMP #$03
    branch CONTACT_DONE
    JMP CONTACT_LOOP
CONTACT_DONE:
    RTS
PMG_DRAW:
    LDX OLD_Y
    LDA #$00
    STA $BC00
    STA $BC01
    STA $BC02
    STA $BC03
    STA $BC04
    STA $BC05
    STA $BC06
    STA $BC07
    LDA POS_YH
    STA PIX_HI
    LDA POS_Y
    STA PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LDA PIX_LO
    CLC
    ADC #$20
    STA OLD_Y
    TAX
    LDA #$60
    STA $BC00
    LDA #$F0
    STA $BC01
    LDA #$60
    STA $BC02
    LDA #$F0
    STA $BC03
    LDA #$60
    STA $BC04
    LDA #$90
    STA $BC05
    LDA #$90
    STA $BC06
    LDA #$00
    STA $BC07
    LDA POS_XH
    STA PIX_HI
    LDA POS_X
    STA PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LSR PIX_HI
    ROR PIX_LO
    LDA PIX_LO
    CLC
    ADC #$30
    STA $D000
    RTS
POS_X:
    .BYTE $00
POS_XH:
    .BYTE $00
POS_Y:
    .BYTE $00
POS_YH:
    .BYTE $00
MOTION_CLOCK:
    .BYTE $00
UPDATES:
    .BYTE $00
JOY:
    .BYTE $00
SIGN_X:
    .BYTE $00
SIGN_Y:
    .BYTE $00
SIGN:
    .BYTE $00
SPEED:
    .BYTE $00
DIAGONAL:
    .BYTE $00
AXIS:
    .BYTE $00
REMAIN:
    .BYTE $00
BLOCKED:
    .BYTE $00
BLOCK_X:
    .BYTE $00
CHUNK:
    .BYTE $00
AMOUNT:
    .BYTE $00
SAVE_LO:
    .BYTE $00
SAVE_HI:
    .BYTE $00
LOW:
    .BYTE $00
HIGH:
    .BYTE $00
MID:
    .BYTE $00
TMP_LO:
    .BYTE $00
TMP_HI:
    .BYTE $00
LEFT:
    .BYTE $00
RIGHT:
    .BYTE $00
TOP:
    .BYTE $00
BOTTOM:
    .BYTE $00
OLD_ROOM:
    .BYTE $00
CONTACT_ID:
    .BYTE $00
ENEMY_LO:
    .BYTE $00
ENEMY_HI:
    .BYTE $00
DIFF_LO:
    .BYTE $00
DIFF_HI:
    .BYTE $00
OLD_Y:
    .BYTE $00
PIX_LO:
    .BYTE $00
PIX_HI:
    .BYTE $00
