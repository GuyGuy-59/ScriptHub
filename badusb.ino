#include <Keyboard.h>

const char AltGrazerty[] PROGMEM = "~#{[|`\\^@#]}";
const char shiftazerty[] PROGMEM = "QBCDEFGHIJKL?NOPARSTUVZXYW1234567890 Q+QQQQM%Q./Q>";
const char azerty[] PROGMEM = "qbcdefghijkl,noparstuvzxyw&q\"'(-q_qq )=q$q*mqq;:!<";
const byte scancode[] PROGMEM = {4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,44,45,46,47,48,49,50,51,52,53,54,55,56,100}; 

const int tempo = 500;


int indexOfPGM(const char *pstr, char c) {
  for (int i = 0; ; ++i) {
    char cc = pgm_read_byte(pstr + i);
    if (cc == '\0') return -1;
    if (cc == c) return i;
  }
}

void Keyfr(const String &Texte) {
  for (unsigned int i = 0; i < Texte.length(); i++) {
    char c = Texte.charAt(i);

    if (c == '\t') {
      Keyboard.write(KEY_TAB);
      continue;
    }

    int idx = indexOfPGM(azerty, c);
    if (idx > -1) {
      byte code = pgm_read_byte(&scancode[idx]) + 136;
      Keyboard.write(code);
      continue;
    }

    idx = indexOfPGM(shiftazerty, c);
    if (idx > -1) {
      byte code = pgm_read_byte(&scancode[idx]) + 136;
      Keyboard.press(KEY_LEFT_SHIFT);
      Keyboard.press(code);
      Keyboard.releaseAll();
      continue;
    }

    idx = indexOfPGM(AltGrazerty, c);
    if (idx > -1) {
      byte code = pgm_read_byte(&scancode[idx + 27]) + 136;
      Keyboard.press(KEY_LEFT_CTRL);
      Keyboard.press(KEY_LEFT_ALT);
      Keyboard.write(code);
      Keyboard.releaseAll();
      if (idx == 0 || idx == 7) { // ~ ou ^
        Keyboard.press(KEY_LEFT_CTRL);
        Keyboard.press(KEY_LEFT_ALT);
        Keyboard.write(code);
        Keyboard.releaseAll();
        Keyboard.write(KEY_BACKSPACE);
      }
    }
  }
}

inline void Keyfrln(const String &Texte) {
  Keyfr(Texte);
  Keyboard.write(KEY_RETURN);
}

void Keycombi(byte key1, char key2) {
  Keyboard.press(key1);
  if ((byte)key2 < 128) {
    Keyfr(String(key2));
  } else {
    Keyboard.press((byte)key2);
  }
  Keyboard.releaseAll();
  delay(tempo);
}

struct KeyCmd {
  const char *cmd; 
  byte mod;
  char key;
};

const KeyCmd cmds[] PROGMEM = {
  {"window+r",   KEY_LEFT_GUI,  'r'},
  {"copier",     KEY_LEFT_CTRL, 'c'},
  {"couper",     KEY_LEFT_CTRL, 'x'},
  {"coller",     KEY_LEFT_CTRL, 'v'},
  {"selectionner", KEY_LEFT_CTRL, 'a'},
  {"annuler",    KEY_LEFT_CTRL, 'z'},
  {"rétablir",   KEY_LEFT_CTRL, 'y'},
  {"imprimer",   KEY_LEFT_CTRL, 'p'}
};

void Keyspecial(const String &Texte) {
  for (uint8_t i = 0; i < sizeof(cmds) / sizeof(cmds[0]); ++i) {
    char buf[14]; 
    strncpy_P(buf, (PGM_P)pgm_read_ptr(&cmds[i].cmd), sizeof(buf));
    if (Texte.equals(buf)) {
      Keycombi(pgm_read_byte(&cmds[i].mod), pgm_read_byte(&cmds[i].key));
      return;
    }
  }
  if (Texte == "fermer") {
    Keycombi(KEY_LEFT_ALT, KEY_F4);
  } else if (Texte == "menufermer") {
    Keycombi(KEY_LEFT_ALT, ' ');
    Keyfr("f");
  }
}

void Key(const String &Texte){
  if      (Texte == "entree")  Keyboard.write(KEY_RETURN);
  else if (Texte == "echap")   Keyboard.write(KEY_ESC);
  else if (Texte == "retour")  Keyboard.write(KEY_BACKSPACE);
  else if (Texte == "droite")  Keyboard.write(KEY_RIGHT_ARROW);
  else if (Texte == "gauche")  Keyboard.write(KEY_LEFT_ARROW);
  else if (Texte == "haut")    Keyboard.write(KEY_UP_ARROW);
  else if (Texte == "bas")     Keyboard.write(KEY_DOWN_ARROW);
  else if (Texte == "f1")      Keyboard.write(KEY_F1);
}

void setup() {
  delay(8000);
  Keyboard.begin();
}

void loop() {
  static bool ran = false;
  if (!ran) {
    ran = true;
    Keyspecial("window+r");
    Keyfrln("");
    delay(2000);
    Keyfr("http:/exampe.org");
    Key("entree");
    delay(50000);
    Keyspecial("fermer");
    Keyboard.end();
  }
}
