loop
areadsensor v
if(v! = "x")
	rdata v a b c
	send c 21
end
delay 1000