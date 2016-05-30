#include <stdio.h>

template<class T, int N>
class Thing {
 public:
  Thing(T obj) : obj_(obj) {
  }

  int getN() {
    return N;
  }

  T get() {
    return obj_;
  }
 private:
  T obj_;
};

template<> ref class Thing<int, 42>;

int main(int argc, char* argv[]) {
  Thing<int> ta(0);

  printf("%d, %d\n", ta.getN(), ta.get());
  return 0;
}