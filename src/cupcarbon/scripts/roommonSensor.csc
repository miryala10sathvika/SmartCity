loop
areadsensor v
if(v! = "x")
	rdata v a b c
	send c 22
end
delay 1000