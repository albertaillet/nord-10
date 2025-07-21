LDA (76032  % Enable for interrupts on level
TRR PIE     % 1, 3, 4, 10, 11, 12, 13 and 14
LDA (3736   % Enable for all internal
TRR         % Interrupt sources except for the Z indicator
LDA 
(P1
IRW
10DP
LDA
(P3
IRW 30DP
etc. for SP
in use
TRA
TRA
IIC
PEA
ION
JMP START