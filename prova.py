import zlib
import sys

a = "this string needs compressing"
print("1.")
print(sys.getsizeof(a))
a = a.encode("zlib")

print("2.")
print(sys.getsizeof(a))
print(a.decode("zlib")) #outputs original contents of a