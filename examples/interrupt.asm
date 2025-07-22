% Example from ND-06.009.01 I.2.6
% INITIALIZATION OF THE INTERRUPT SYSTEM
	LDA	(76032	% Enable for interrupts on level
	TRR	PIE	% 1, 3, 4, 10, 11, 12, 13 and 14
	LDA	(3736	% Enable for all internal
	TRR	IIE	% Interrupt sources except for the Z indicator

	LDA	(P1	% The saved program counters
	IRW	10DP	% on the enabled levels
	LDA	(P3	% start value
	IRW	30DP	% etc. for SP in use
	TRA	IIC	% Unlock IIC
	TRA	PEA	% Unlock PEA and PES
	ION		% Turn on interrupt system	
	JMP START	% Go to main program