// by Thomas Rogg

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main()
{
	char v[197], v2[197];
	int i;

	memset(v, ' ', sizeof(v));
	v[100] = 'x';
	v[196] = 0;

	while(1)
	{
		for(i = 0; i < sizeof(v) - 1; i++)
		{
			int c = (v[(i + 195) % 196] == 'x' ? 1 : 0)
                        + (v[(i + 196) % 196] == 'x' ? 1 : 0)
                        + (v[(i + 197) % 196] == 'x' ? 1 : 0);
			if(c == 1 || c == 2)
				v2[i] = 'x';
			else
				v2[i] = ' ';
		}
		v2[196] = 0;

		printf("%s\n", v2);
		memcpy(v, v2, sizeof(v));
		usleep(100000);
	}
}
