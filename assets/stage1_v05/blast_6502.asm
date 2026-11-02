; tools/build_stage1_v05.py is authoritative
INIT:
    ; $7800
    LDA #0
    ; $7802
    STA absolute
    ; $7805
    STA LIVE
    ; $7808
    STA OLD_COUNT
    ; $780B
    STA SOUND
    ; $780E
    STA absolute
    ; $7811
    JSR core init+5
    ; $7814
    JSR V_ALIGN
    ; $7817
    LDA absolute
    ; $781A
    STA V_MOTION_CLOCK
    ; $781D
    LDA #
    ; $781F
    STA V_OLD_Y
    ; $7822
    LDX #0
CLEAR_PMG:
    ; $7824
    STA PMG,X
    ; $7827
    STA PMG,X
    ; $782A
    STA PMG,X
    ; $782D
    STA PMG,X
    ; $7830
    STA PMG,X
    ; $7833
    STA PMG,X
    ; $7836
    STA PMG,X
    ; $7839
    STA PMG,X
    ; $783C
    INX
    ; $783D
    conditional jump CLEAR_PMG
    ; $7842
    LDA #
    ; $7844
    STA absolute
    ; $7847
    LDA #
    ; $7849
    STA absolute
    ; $784C
    LDA #
    ; $784E
    STA absolute
    ; $7851
    LDA #
    ; $7853
    STA absolute
    ; $7856
    LDA #
    ; $7858
    STA absolute
    ; $785B
    LDA #
    ; $785D
    STA absolute
    ; $7860
    LDA #
    ; $7862
    STA absolute
    ; $7865
    LDA #
    ; $7867
    STA absolute
    ; $786A
    LDA #
    ; $786C
    STA absolute
    ; $786F
    LDA #
    ; $7871
    STA absolute
    ; $7874
    LDA #
    ; $7876
    STA absolute
    ; $7879
    LDA #
    ; $787B
    STA absolute
    ; $787E
    LDA #
    ; $7880
    STA absolute
    ; $7883
    LDA #
    ; $7885
    LDX #
CLEAR_STATE:
    ; $7887
    STA state,X
    ; $788A
    DEX
    ; $788B
    CPX #255
    ; $788D
    conditional jump CLEAR_STATE
    ; $7892
    LDA #
    ; $7894
    STA CHARGES
    ; $7897
    LDA #
    ; $7899
    STA REFILL
    ; $789C
    LDA #
    ; $789E
    STA AIM
    ; $78A1
    STA LAST_AIM
    ; $78A4
    LDA #
    ; $78A6
    STA HELD
    ; $78A9
    STA SPENT
    ; $78AC
    LDA absolute
    ; $78AF
    STA CLOCK
    ; $78B2
    LDA #
    ; $78B4
    STA absolute
    ; $78B7
    JSR V_PMG_DRAW
    ; $78BA
    RTS
INPUT:
    ; $78BB
    LDA absolute
    ; $78BE
    SEC
    ; $78BF
    SBC CLOCK
    ; $78C2
    conditional jump TICK
    ; $78C7
    RTS
TICK:
    ; $78C8
    STA DELTA
    ; $78CB
    LDA absolute
    ; $78CE
    STA CLOCK
    ; $78D1
    LDA #
    ; $78D3
    STA C_SEP_0
    ; $78D6
    STA C_SEP_1
    ; $78D9
    STA C_SEP_2
    ; $78DC
    LDA COOL
    ; $78DF
    conditional jump T_30940
    ; $78E4
    SEC
    ; $78E5
    SBC DELTA
    ; $78E8
    conditional jump T_30940_S
    ; $78ED
    LDA #
T_30940_S:
    ; $78EF
    STA COOL
T_30940:
    ; $78F2
    LDA RECOVER
    ; $78F5
    conditional jump T_30962
    ; $78FA
    SEC
    ; $78FB
    SBC DELTA
    ; $78FE
    conditional jump T_30962_S
    ; $7903
    LDA #
T_30962_S:
    ; $7905
    STA RECOVER
T_30962:
    ; $7908
    LDA LIVE
    ; $790B
    conditional jump T_30984
    ; $7910
    SEC
    ; $7911
    SBC DELTA
    ; $7914
    conditional jump T_30984_S
    ; $7919
    LDA #
T_30984_S:
    ; $791B
    STA LIVE
T_30984:
    ; $791E
    LDA SOUND
    ; $7921
    conditional jump T_31006
    ; $7926
    SEC
    ; $7927
    SBC DELTA
    ; $792A
    conditional jump T_31006_S
    ; $792F
    LDA #
T_31006_S:
    ; $7931
    STA SOUND
T_31006:
    ; $7934
    LDA CHARGES
    ; $7937
    CMP #
    ; $7939
    conditional jump REFILL_FULL
    ; $793E
    LDA REFILL
    ; $7941
    conditional jump T_31038
    ; $7946
    SEC
    ; $7947
    SBC DELTA
    ; $794A
    conditional jump T_31038_S
    ; $794F
    LDA #
T_31038_S:
    ; $7951
    STA REFILL
T_31038:
    ; $7954
    LDA REFILL
    ; $7957
    conditional jump REFILL_DONE
    ; $795C
    INC CHARGES
    ; $795F
    LDA #
    ; $7961
    STA REFILL
    ; $7964
    JMP REFILL_DONE
REFILL_FULL:
    ; $7967
    LDA #
    ; $7969
    STA REFILL
REFILL_DONE:
    ; $796C
    JSR PUSH_FRAME
    ; $796F
    JSR SFX
    ; $7972
    LDA absolute
    ; $7975
    AND #1
    ; $7977
    conditional jump FIRE
    ; $797C
    LDA #
    ; $797E
    STA HELD
    ; $7981
    STA SPENT
    ; $7984
    STA WIND
    ; $7987
    LDA #
    ; $7989
    STA LAST_AIM
    ; $798C
    LDA RECOVER
    ; $798F
    conditional jump STAY
    ; $7994
    JSR V_MOVE
    ; $7997
    JMP EFFECTS
FIRE:
    ; $799A
    LDA absolute
    ; $799D
    STA V_MOTION_CLOCK
    ; $79A0
    LDA HELD
    ; $79A3
    conditional jump AIMING
    ; $79A8
    LDA #
    ; $79AA
    STA HELD
    ; $79AD
    LDA #
    ; $79AF
    STA SPENT
    ; $79B2
    LDA COOL
    ; $79B5
    conditional jump BLOCK_HOLD
    ; $79BA
    LDA CHARGES
    ; $79BD
    conditional jump AIMING
BLOCK_HOLD:
    ; $79C2
    LDA #
    ; $79C4
    STA SPENT
AIMING:
    ; $79C7
    LDA absolute
    ; $79CA
    AND #15
    ; $79CC
    TAX
    ; $79CD
    LDA joy table,X
    ; $79D0
    STA AIM
    ; $79D3
    CMP #
    ; $79D5
    conditional jump VALID_AIM
    ; $79DA
    LDA #
    ; $79DC
    STA WIND
    ; $79DF
    LDA #
    ; $79E1
    STA LAST_AIM
    ; $79E4
    JMP STAY
VALID_AIM:
    ; $79E7
    LDA SPENT
    ; $79EA
    conditional jump STAY
    ; $79EF
    LDA AIM
    ; $79F2
    CMP LAST_AIM
    ; $79F5
    conditional jump STABLE
    ; $79FA
    STA LAST_AIM
    ; $79FD
    LDA #
    ; $79FF
    STA WIND
    ; $7A02
    JMP WIND_CHECK
STABLE:
    ; $7A05
    LDA WIND
    ; $7A08
    CLC
    ; $7A09
    ADC DELTA
    ; $7A0C
    STA WIND
WIND_CHECK:
    ; $7A0F
    LDA WIND
    ; $7A12
    CMP #
    ; $7A14
    conditional jump STAY
    ; $7A19
    JSR DISCHARGE
STAY:
    ; $7A1C
    LDA absolute
    ; $7A1F
    STA V_MOTION_CLOCK
    ; $7A22
    JSR V_PMG_DRAW
EFFECTS:
    ; $7A25
    LDA LIVE
    ; $7A28
    conditional jump INPUT_DONE
    ; $7A2D
    LDA C_ROOM
    ; $7A30
    CMP CLOUD_ROOM
    ; $7A33
    conditional jump INPUT_DONE
    ; $7A38
    JSR HITS
INPUT_DONE:
    ; $7A3B
    RTS
DISCHARGE:
    ; $7A3C
    LDA #
    ; $7A3E
    STA SPENT
    ; $7A41
    DEC CHARGES
    ; $7A44
    LDA #
    ; $7A46
    STA COOL
    ; $7A49
    LDA #
    ; $7A4B
    STA RECOVER
    ; $7A4E
    LDA #
    ; $7A50
    STA LIVE
    ; $7A53
    LDA #
    ; $7A55
    STA SOUND
    ; $7A58
    LDA C_ROOM
    ; $7A5B
    STA CLOUD_ROOM
    ; $7A5E
    LDA C_PX
    ; $7A61
    STA ORIGIN_X
    ; $7A64
    LDA C_PY
    ; $7A67
    STA ORIGIN_Y
    ; $7A6A
    LDA #
    ; $7A6C
    STA hit
    ; $7A6F
    STA hit
    ; $7A72
    STA hit
    ; $7A75
    LDA AIM
    ; $7A78
    STA BURST_AIM
    ; $7A7B
    ASL
    ; $7A7C
    ASL
    ; $7A7D
    ASL
    ; $7A7E
    SEC
    ; $7A7F
    SBC AIM
    ; $7A82
    STA DIR_BASE
    ; $7A85
    LDA #
    ; $7A87
    STA CELL
MAKE_CELL:
    ; $7A8A
    LDA DIR_BASE
    ; $7A8D
    CLC
    ; $7A8E
    ADC CELL
    ; $7A91
    STA GLOBAL_CELL
    ; $7A94
    TAX
    ; $7A95
    LDA off X
    ; $7A98
    CLC
    ; $7A99
    ADC ORIGIN_X
    ; $7A9C
    LDX CELL
    ; $7A9F
    STA,X CLOUD_X
    ; $7AA2
    LDX GLOBAL_CELL
    ; $7AA5
    LDA off Y
    ; $7AA8
    CLC
    ; $7AA9
    ADC ORIGIN_Y
    ; $7AAC
    LDX CELL
    ; $7AAF
    STA,X CLOUD_Y
    ; $7AB2
    JSR LOS
    ; $7AB5
    LDX CELL
    ; $7AB8
    STA,X VALID
    ; $7ABB
    INC CELL
    ; $7ABE
    LDA CELL
    ; $7AC1
    CMP #
    ; $7AC3
    conditional jump MAKE_CELL
    ; $7AC8
    JSR SFX
    ; $7ACB
    RTS
LOS:
    ; $7ACC
    LDA CLOUD_ROOM
    ; $7ACF
    STA C_LOOK_ROOM
    ; $7AD2
    LDX CELL
    ; $7AD5
    LDA,X CLOUD_X
    ; $7AD8
    STA C_NX
    ; $7ADB
    LDA,X CLOUD_Y
    ; $7ADE
    STA C_NY
    ; $7AE1
    JSR C_RAY_WALK
    ; $7AE4
    conditional jump LOS_BAD
    ; $7AE9
    LDX GLOBAL_CELL
    ; $7AEC
    LDA path length
    ; $7AEF
    STA PATH_LEN
    ; $7AF2
    conditional jump LOS_HAS_PATH
    ; $7AF7
    LDA #
    ; $7AF9
    RTS
LOS_HAS_PATH:
    ; $7AFA
    LDA GLOBAL_CELL
    ; $7AFD
    LSR
    ; $7AFE
    LSR
    ; $7AFF
    LSR
    ; $7B00
    LSR
    ; $7B01
    CLC
    ; $7B02
    ADC #
    ; $7B04
    STA zp
    ; $7B06
    LDA GLOBAL_CELL
    ; $7B09
    ASL
    ; $7B0A
    ASL
    ; $7B0B
    ASL
    ; $7B0C
    ASL
    ; $7B0D
    STA zp
    ; $7B0F
    LDA #
    ; $7B11
    STA PATH_POS
LOS_LOOP:
    ; $7B14
    LDA PATH_POS
    ; $7B17
    ASL
    ; $7B18
    TAY
    ; $7B19
    LDA indirect,Y
    ; $7B1B
    CLC
    ; $7B1C
    ADC ORIGIN_X
    ; $7B1F
    STA C_NX
    ; $7B22
    INY
    ; $7B23
    LDA indirect,Y
    ; $7B25
    CLC
    ; $7B26
    ADC ORIGIN_Y
    ; $7B29
    STA C_NY
    ; $7B2C
    JSR C_RAY_WALK
    ; $7B2F
    conditional jump LOS_BAD
    ; $7B34
    INC PATH_POS
    ; $7B37
    LDA PATH_POS
    ; $7B3A
    CMP PATH_LEN
    ; $7B3D
    conditional jump LOS_LOOP
    ; $7B42
    LDA #
    ; $7B44
    RTS
LOS_BAD:
    ; $7B45
    LDA #
    ; $7B47
    RTS
GET_COUNT:
    ; $7B48
    LDA #
    ; $7B4A
    STA COUNT
    ; $7B4D
    LDA LIVE
    ; $7B50
    conditional jump COUNT_DONE
    ; $7B55
    CMP #
    ; $7B57
    conditional jump COUNT_ONE
    ; $7B5C
    CMP #
    ; $7B5E
    conditional jump COUNT_FOUR
    ; $7B63
    LDA #
    ; $7B65
    JMP COUNT_SET
COUNT_FOUR:
    ; $7B68
    LDA #
    ; $7B6A
    JMP COUNT_SET
COUNT_ONE:
    ; $7B6D
    LDA #
COUNT_SET:
    ; $7B6F
    STA COUNT
COUNT_DONE:
    ; $7B72
    RTS
HITS:
    ; $7B73
    JSR GET_COUNT
    ; $7B76
    LDA #
    ; $7B78
    STA INDEX
HIT_WORKER:
    ; $7B7B
    LDX INDEX
    ; $7B7E
    LDA,X C_E_ACTIVE
    ; $7B81
    conditional jump HIT_NEXT
    ; $7B86
    LDA,X HIT
    ; $7B89
    conditional jump HIT_NEXT
    ; $7B8E
    LDA,X C_E_EROOM
    ; $7B91
    CMP CLOUD_ROOM
    ; $7B94
    conditional jump HIT_NEXT
    ; $7B99
    LDA #
    ; $7B9B
    STA CELL
HIT_CELL:
    ; $7B9E
    LDX CELL
    ; $7BA1
    LDA,X VALID
    ; $7BA4
    conditional jump HIT_CELL_NEXT
    ; $7BA9
    LDA,X CLOUD_X
    ; $7BAC
    STA TEST_X
    ; $7BAF
    LDA,X CLOUD_Y
    ; $7BB2
    STA TEST_Y
    ; $7BB5
    LDX INDEX
    ; $7BB8
    LDA,X C_E_EX
    ; $7BBB
    CMP TEST_X
    ; $7BBE
    conditional jump HIT_CELL_NEXT
    ; $7BC3
    LDA,X C_E_EY
    ; $7BC6
    CMP TEST_Y
    ; $7BC9
    conditional jump HIT_CELL_NEXT
    ; $7BCE
    LDA #
    ; $7BD0
    STA,X HIT
    ; $7BD3
    LDA #
    ; $7BD5
    STA,X PUSH
    ; $7BD8
    LDA #
    ; $7BDA
    STA,X PUSH_TIME
    ; $7BDD
    LDA #
    ; $7BDF
    CLC
    ; $7BE0
    ADC C_ELAPSED
    ; $7BE3
    STA,X C_E_STUN
    ; $7BE6
    LDA #
    ; $7BE8
    STA,X C_E_SEPARATE
    ; $7BEB
    JMP HIT_NEXT
HIT_CELL_NEXT:
    ; $7BEE
    INC CELL
    ; $7BF1
    LDA CELL
    ; $7BF4
    CMP COUNT
    ; $7BF7
    conditional jump HIT_CELL
HIT_NEXT:
    ; $7BFC
    INC INDEX
    ; $7BFF
    LDA INDEX
    ; $7C02
    CMP #
    ; $7C04
    conditional jump HIT_WORKER
    ; $7C09
    RTS
PUSH_FRAME:
    ; $7C0A
    LDA #
    ; $7C0C
    STA PUSH_ID
PUSH_WORKER:
    ; $7C0F
    LDX PUSH_ID
    ; $7C12
    LDA,X BONK
    ; $7C15
    conditional jump NO_BONK_TICK
    ; $7C1A
    SEC
    ; $7C1B
    SBC DELTA
    ; $7C1E
    conditional jump BONK_SAVE
    ; $7C23
    LDA #
BONK_SAVE:
    ; $7C25
    STA,X BONK
NO_BONK_TICK:
    ; $7C28
    LDA,X PUSH
    ; $7C2B
    conditional jump PUSH_NEXT
    ; $7C30
    LDA,X PUSH_TIME
    ; $7C33
    SEC
    ; $7C34
    SBC DELTA
    ; $7C37
    conditional jump PUSH_STEP
    ; $7C3C
    STA,X PUSH_TIME
    ; $7C3F
    conditional jump PUSH_NEXT
PUSH_STEP:
    ; $7C44
    LDA PUSH_ID
    ; $7C47
    STA C_CURRENT
    ; $7C4A
    JSR C_LOAD_WORKER
    ; $7C4D
    LDA C_EROOM
    ; $7C50
    STA C_LOOK_ROOM
    ; $7C53
    LDA C_EX
    ; $7C56
    STA SAVE_X
    ; $7C59
    LDA C_EY
    ; $7C5C
    STA SAVE_Y
    ; $7C5F
    LDX BURST_AIM
    ; $7C62
    LDA DX
    ; $7C65
    CLC
    ; $7C66
    ADC SAVE_X
    ; $7C69
    STA DEST_X
    ; $7C6C
    LDX BURST_AIM
    ; $7C6F
    LDA DY
    ; $7C72
    CLC
    ; $7C73
    ADC SAVE_Y
    ; $7C76
    STA DEST_Y
    ; $7C79
    LDA #
    ; $7C7B
    STA C_WHO
    ; $7C7E
    LDA DEST_X
    ; $7C81
    STA C_NX
    ; $7C84
    LDA SAVE_Y
    ; $7C87
    STA C_NY
    ; $7C8A
    JSR PUSH_TILE
    ; $7C8D
    CMP #
    ; $7C8F
    conditional jump WORKER_IMPACT
    ; $7C94
    CMP #
    ; $7C96
    conditional jump PUSH_BONK
    ; $7C9B
    LDA SAVE_X
    ; $7C9E
    STA C_NX
    ; $7CA1
    LDA DEST_Y
    ; $7CA4
    STA C_NY
    ; $7CA7
    JSR PUSH_TILE
    ; $7CAA
    CMP #
    ; $7CAC
    conditional jump WORKER_IMPACT
    ; $7CB1
    CMP #
    ; $7CB3
    conditional jump PUSH_BONK
    ; $7CB8
    LDA DEST_X
    ; $7CBB
    STA C_NX
    ; $7CBE
    LDA DEST_Y
    ; $7CC1
    STA C_NY
    ; $7CC4
    JSR PUSH_TILE
    ; $7CC7
    CMP #
    ; $7CC9
    conditional jump WORKER_IMPACT
    ; $7CCE
    CMP #
    ; $7CD0
    conditional jump PUSH_BONK
    ; $7CD5
    JMP PUSH_GO
WORKER_IMPACT:
    ; $7CD8
    LDX C_OCC_ID
    ; $7CDB
    LDA #
    ; $7CDD
    CLC
    ; $7CDE
    ADC C_ELAPSED
    ; $7CE1
    STA TEST_X
    ; $7CE4
    LDA,X C_E_STUN
    ; $7CE7
    CMP TEST_X
    ; $7CEA
    conditional jump STAGGER_KEPT
    ; $7CEF
    LDA TEST_X
    ; $7CF2
    STA,X C_E_STUN
STAGGER_KEPT:
    ; $7CF5
    LDA #
    ; $7CF7
    STA,X BONK
    ; $7CFA
    JMP PUSH_BONK
PUSH_GO:
    ; $7CFD
    LDA DEST_X
    ; $7D00
    STA C_EX
    ; $7D03
    LDA DEST_Y
    ; $7D06
    STA C_EY
    ; $7D09
    JSR C_SAVE_WORKER
    ; $7D0C
    LDX PUSH_ID
    ; $7D0F
    LDA,X PUSH
    ; $7D12
    CLC
    ; $7D13
    ADC #
    ; $7D15
    STA,X PUSH
    ; $7D18
    LDA #
    ; $7D1A
    STA,X PUSH_TIME
    ; $7D1D
    JMP PUSH_NEXT
PUSH_BONK:
    ; $7D20
    LDX PUSH_ID
    ; $7D23
    LDA #
    ; $7D25
    STA,X PUSH
    ; $7D28
    LDA #
    ; $7D2A
    STA,X BONK
    ; $7D2D
    LDA #
    ; $7D2F
    CLC
    ; $7D30
    ADC C_ELAPSED
    ; $7D33
    STA,X C_E_STUN
PUSH_NEXT:
    ; $7D36
    INC PUSH_ID
    ; $7D39
    LDA PUSH_ID
    ; $7D3C
    CMP #
    ; $7D3E
    conditional jump PUSH_WORKER
    ; $7D43
    LDA C_ROOM
    ; $7D46
    STA C_LOOK_ROOM
    ; $7D49
    RTS
PUSH_TILE:
    ; $7D4A
    JSR C_RAY_WALK
    ; $7D4D
    conditional jump PUSH_TILE_WALK
    ; $7D52
    RTS
PUSH_TILE_WALK:
    ; $7D53
    JSR C_OCCUPIED
    ; $7D56
    conditional jump PUSH_TILE_EMPTY
    ; $7D5B
    LDA #
    ; $7D5D
    RTS
PUSH_TILE_EMPTY:
    ; $7D5E
    LDA #
    ; $7D60
    RTS
DYNAMIC:
    ; $7D61
    LDA CLOUD_ROOM
    ; $7D64
    CMP C_ROOM
    ; $7D67
    conditional jump DYNAMIC_CORE
    ; $7D6C
    LDA #
    ; $7D6E
    STA CELL
RESTORE_LOOP:
    ; $7D71
    LDA CELL
    ; $7D74
    CMP OLD_COUNT
    ; $7D77
    conditional jump DYNAMIC_CORE
    ; $7D7C
    LDX CELL
    ; $7D7F
    LDA,X VALID
    ; $7D82
    conditional jump RESTORE_NEXT
    ; $7D87
    LDA,X CLOUD_X
    ; $7D8A
    STA C_NX
    ; $7D8D
    LDA,X CLOUD_Y
    ; $7D90
    STA C_NY
    ; $7D93
    JSR C_RESTORE_CELL
RESTORE_NEXT:
    ; $7D96
    INC CELL
    ; $7D99
    JMP RESTORE_LOOP
DYNAMIC_CORE:
    ; $7D9C
    LDA #
    ; $7D9E
    STA C_DRAW_ID
    ; $7DA1
    JSR old dynamic+5
    ; $7DA4
    RTS
STATUS:
    ; $7DA5
    JSR STATUS_COPY
    ; $7DA8
    LDA C_STATE
    ; $7DAB
    conditional jump STATUS_PLAY
    ; $7DB0
    LDA #
    ; $7DB2
    STA SOUND
    ; $7DB5
    STA absolute
    ; $7DB8
    RTS
STATUS_PLAY:
    ; $7DB9
    JSR GET_COUNT
    ; $7DBC
    LDA #
    ; $7DBE
    STA OLD_COUNT
    ; $7DC1
    LDA CLOUD_ROOM
    ; $7DC4
    CMP C_ROOM
    ; $7DC7
    conditional jump HUD
    ; $7DCC
    LDA COUNT
    ; $7DCF
    STA OLD_COUNT
    ; $7DD2
    LDA #
    ; $7DD4
    STA CELL
DRAW_CLOUD:
    ; $7DD7
    LDA CELL
    ; $7DDA
    CMP COUNT
    ; $7DDD
    conditional jump HUD
    ; $7DE2
    LDX CELL
    ; $7DE5
    LDA,X VALID
    ; $7DE8
    conditional jump DRAW_CLOUD_NEXT
    ; $7DED
    LDA,X CLOUD_X
    ; $7DF0
    STA C_NX
    ; $7DF3
    LDA,X CLOUD_Y
    ; $7DF6
    STA C_NY
    ; $7DF9
    LDA LIVE
    ; $7DFC
    AND
    ; $7DFE
    CLC
    ; $7DFF
    ADC #
    ; $7E01
    STA C_GLYPH
    ; $7E04
    JSR C_DRAW_ACTOR
DRAW_CLOUD_NEXT:
    ; $7E07
    INC CELL
    ; $7E0A
    JMP DRAW_CLOUD
HUD:
    ; $7E0D
    LDA #
    ; $7E0F
    STA INDEX
BONK_DRAW:
    ; $7E12
    LDX INDEX
    ; $7E15
    LDA,X C_E_ACTIVE
    ; $7E18
    conditional jump BONK_NEXT
    ; $7E1D
    LDA,X BONK
    ; $7E20
    conditional jump BONK_NEXT
    ; $7E25
    LDA,X C_E_EROOM
    ; $7E28
    CMP C_ROOM
    ; $7E2B
    conditional jump BONK_NEXT
    ; $7E30
    LDA,X C_E_EX
    ; $7E33
    STA C_NX
    ; $7E36
    LDA,X C_E_EY
    ; $7E39
    STA C_NY
    ; $7E3C
    LDA #
    ; $7E3E
    STA C_GLYPH
    ; $7E41
    JSR C_DRAW_ACTOR
BONK_NEXT:
    ; $7E44
    INC INDEX
    ; $7E47
    LDA INDEX
    ; $7E4A
    CMP #
    ; $7E4C
    conditional jump BONK_DRAW
    ; $7E51
    LDA CHARGES
    ; $7E54
    CLC
    ; $7E55
    ADC #
    ; $7E57
    STA absolute
    ; $7E5A
    LDA CHARGES
    ; $7E5D
    conditional jump HUD_EMPTY
    ; $7E62
    LDA COOL
    ; $7E65
    conditional jump HUD_COOL
    ; $7E6A
    LDA #
    ; $7E6C
    JMP HUD_TEXT
HUD_EMPTY:
    ; $7E6F
    LDA #
    ; $7E71
    JMP HUD_TEXT
HUD_COOL:
    ; $7E74
    LDA #
HUD_TEXT:
    ; $7E76
    STA SOUND_INDEX
    ; $7E79
    LDA #
    ; $7E7B
    STA CELL
HUD_LOOP:
    ; $7E7E
    LDA SOUND_INDEX
    ; $7E81
    CLC
    ; $7E82
    ADC CELL
    ; $7E85
    TAX
    ; $7E86
    LDA HUD text
    ; $7E89
    LDX CELL
    ; $7E8C
    STA HUD,X
    ; $7E8F
    INC CELL
    ; $7E92
    LDA CELL
    ; $7E95
    CMP #
    ; $7E97
    conditional jump HUD_LOOP
STATUS_DONE:
    ; $7E9C
    RTS
STATUS_COPY:
    ; $7E9D
    original footer bytes
SFX:
    ; $7ECF
    LDA SOUND
    ; $7ED2
    conditional jump SFX_NOTE
    ; $7ED7
    LDA #
    ; $7ED9
    STA absolute
    ; $7EDC
    RTS
SFX_NOTE:
    ; $7EDD
    CLC
    ; $7EDE
    ADC #
    ; $7EE0
    TAX
    ; $7EE1
    LDA whoosh frequency
    ; $7EE4
    STA absolute
    ; $7EE7
    LDA whoosh volume
    ; $7EEA
    STA absolute
    ; $7EED
    RTS
POSE:
    ; $7EEE
    LDX V_OLD_Y
    ; $7EF1
    LDA #
    ; $7EF3
    STA P1 old row
    ; $7EF6
    STA P1 old row
    ; $7EF9
    STA P1 old row
    ; $7EFC
    STA P1 old row
    ; $7EFF
    STA P1 old row
    ; $7F02
    STA P1 old row
    ; $7F05
    STA P1 old row
    ; $7F08
    STA P1 old row
    ; $7F0B
    LDX V_OLD_Y
    ; $7F0E
    JSR old PMG+3
    ; $7F11
    LDA HELD
    ; $7F14
    conditional jump POSE_ACTIVE
    ; $7F19
    LDA RECOVER
    ; $7F1C
    conditional jump POSE_DONE
POSE_ACTIVE:
    ; $7F21
    LDA AIM
    ; $7F24
    CMP #
    ; $7F26
    conditional jump POSE_DONE
    ; $7F2B
    ASL
    ; $7F2C
    ASL
    ; $7F2D
    ASL
    ; $7F2E
    ASL
    ; $7F2F
    STA POSE_PHASE
    ; $7F32
    LDA WIND
    ; $7F35
    AND
    ; $7F37
    ASL
    ; $7F38
    ASL
    ; $7F39
    CLC
    ; $7F3A
    ADC POSE_PHASE
    ; $7F3D
    STA POSE_PHASE
    ; $7F40
    LDA #
    ; $7F42
    STA CELL
POSE_LOOP:
    ; $7F45
    LDA POSE_PHASE
    ; $7F48
    CLC
    ; $7F49
    ADC CELL
    ; $7F4C
    TAX
    ; $7F4D
    LDA pose
    ; $7F50
    STA TEST_X
    ; $7F53
    LDA V_OLD_Y
    ; $7F56
    CLC
    ; $7F57
    ADC CELL
    ; $7F5A
    TAX
    ; $7F5B
    LDA TEST_X
    ; $7F5E
    STA player0
    ; $7F61
    LDA AIM
    ; $7F64
    ASL
    ; $7F65
    ASL
    ; $7F66
    ASL
    ; $7F67
    CLC
    ; $7F68
    ADC CELL
    ; $7F6B
    TAX
    ; $7F6C
    LDA jeans overlay
    ; $7F6F
    STA TEST_X
    ; $7F72
    LDA V_OLD_Y
    ; $7F75
    CLC
    ; $7F76
    ADC CELL
    ; $7F79
    TAX
    ; $7F7A
    LDA TEST_X
    ; $7F7D
    STA player1
    ; $7F80
    INC CELL
    ; $7F83
    LDA CELL
    ; $7F86
    CMP #
    ; $7F88
    conditional jump POSE_LOOP
    ; $7F8D
    LDA absolute
    ; $7F90
    STA absolute
POSE_DONE:
    ; $7F93
    RTS
