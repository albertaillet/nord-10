% Example from ND-06.009.01 I.2.8
% EXTERNAL INTERRUPT IDENTIFICATION
LEV12,	IDENT	PL12	% Identify interrupting device on level 12
	RADD	SADP	% The code is written into the A register, P := P + A
	JMP	ERROR	% Branch to error handler if ident code is zero
	JMP	DRIV1	% Branch to proper driver 1
	JMP	DRIV2	% Branch to proper driver 2
			% etc.
	JMP	DRIVn	% Branch to proper driver n

ERROR,	...		% Ident code equal to zero is not legal

DRIV1,	...		% Start of driver 1 routine
	...			% Driver code continues

% etc.