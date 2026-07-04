#include <Keyboard.h>

const char AltGrazerty[] PROGMEM = "~#{[|`\\^@]}";
const char shiftazerty[] PROGMEM = "QBCDEFGHIJKL?NOPARSTUVZXYW1234567890 Q+QQQQM%Q./Q>";
const char azerty[]      PROGMEM = "qbcdefghijkl,noparstuvzxyw&q\"'(-q_qq )=q$q*mqq;:!<";
const byte scancode[] PROGMEM = {
  4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
  30,31,32,33,34,35,36,37,38,39,
  44,45,46,47,48,49,50,51,52,53,54,55,56,100
};

const int tempo = 500;

// ---------- Helpers PROGMEM ----------
int indexOfPGM(const char *pstr, char c) {
  for (int i = 0; ; ++i) {
    char cc = pgm_read_byte(pstr + i);
    if (cc == '\0') return -1;
    if (cc == c) return i;
  }
}

// ---------- Saisie de texte FR ----------
void Keyfr(const String &Texte) {
  for (unsigned int i = 0; i < Texte.length(); i++) {
    char c = Texte.charAt(i);

    if (c == '\t') {
      Keyboard.write(KEY_TAB);
      continue;
    }
    if (c == ' ') {
      Keyboard.write(' ');
      continue;
    }

    int idx = indexOfPGM(azerty, c);
    if (idx > -1) {
      byte code = pgm_read_byte(&scancode[idx]) + 136;
      Keyboard.write(code);
      delay(5);
      continue;
    }

    idx = indexOfPGM(shiftazerty, c);
    if (idx > -1) {
      byte code = pgm_read_byte(&scancode[idx]) + 136;
      Keyboard.press(KEY_LEFT_SHIFT);
      Keyboard.press(code);
      delay(5);
      Keyboard.releaseAll();
      continue;
    }

    idx = indexOfPGM(AltGrazerty, c);
    if (idx > -1) {
      // Les caractères AltGr correspondent aux touches chiffres + crochets
      // Indices 0..9 -> chiffres (scancode positions 27..36)
      // Indices 10..11 -> ] } (autres positions, à adapter selon ton mapping)
      byte code = pgm_read_byte(&scancode[idx + 27]) + 136;
      Keyboard.press(KEY_RIGHT_ALT); // AltGr = Right Alt
      Keyboard.press(code);
      delay(5);
      Keyboard.releaseAll();

      // ~ et ^ sont des touches mortes : on tape espace après pour valider
      if (c == '~' || c == '^') {
        Keyboard.write(' ');
      }
    }
  }
}

inline void Keyfrln(const String &Texte) {
  Keyfr(Texte);
  Keyboard.write(KEY_RETURN);
}

// ---------- Combinaisons modificateur + touche ----------
void Keycombi(byte key1, char key2) {
  Keyboard.releaseAll();
  delay(50);
  Keyboard.press(key1);
  delay(30);
  Keyboard.press((byte)key2);
  delay(50);
  Keyboard.releaseAll();
  delay(tempo);
}

// ---------- Commandes spéciales ----------
struct KeyCmd {
  const char *cmd;
  byte mod;
  char key;
};

const KeyCmd cmds[] = {
  {"window+r",     KEY_LEFT_GUI,  'r'},
  {"copier",       KEY_LEFT_CTRL, 'c'},
  {"couper",       KEY_LEFT_CTRL, 'x'},
  {"coller",       KEY_LEFT_CTRL, 'v'},
  {"selectionner", KEY_LEFT_CTRL, 'a'},
  {"annuler",      KEY_LEFT_CTRL, 'z'},
  {"retablir",     KEY_LEFT_CTRL, 'y'},
  {"imprimer",     KEY_LEFT_CTRL, 'p'}
};

void Keyspecial(const String &Texte) {
  for (uint8_t i = 0; i < sizeof(cmds) / sizeof(cmds[0]); ++i) {
    if (Texte.equals(cmds[i].cmd)) {
      Keycombi(cmds[i].mod, cmds[i].key);
      return;
    }
  }
  if (Texte == "fermer") {
    Keyboard.releaseAll();
    Keyboard.press(KEY_LEFT_ALT);
    Keyboard.press(KEY_F4);
    delay(50);
    Keyboard.releaseAll();
    delay(tempo);
  } else if (Texte == "menufermer") {
    Keycombi(KEY_LEFT_ALT, ' ');
    delay(200);
    Keyfr("f");
  }
}

// ---------- Touches simples ----------
void Key(const String &Texte) {
  if      (Texte == "entree")  Keyboard.write(KEY_RETURN);
  else if (Texte == "echap")   Keyboard.write(KEY_ESC);
  else if (Texte == "retour")  Keyboard.write(KEY_BACKSPACE);
  else if (Texte == "droite")  Keyboard.write(KEY_RIGHT_ARROW);
  else if (Texte == "gauche")  Keyboard.write(KEY_LEFT_ARROW);
  else if (Texte == "haut")    Keyboard.write(KEY_UP_ARROW);
  else if (Texte == "bas")     Keyboard.write(KEY_DOWN_ARROW);
  else if (Texte == "f1")      Keyboard.write(KEY_F1);
  else if (Texte == "f4")      Keyboard.write(KEY_F4);
  else if (Texte == "tab")     Keyboard.write(KEY_TAB);
  else if (Texte == "espace")  Keyboard.write(' ');
}

// ---------- Setup / Loop ----------
void setup() {
  delay(5000);          // Laisse Windows reconnaître le HID
  Keyboard.begin();
  delay(1000);
}

void loop() {
  static bool ran = false;
  if (!ran) {
    ran = true;

    // Ouvre la boîte Exécuter
    Keyspecial("window+r");
    delay(1000);

    // Tape l'URL et valide
    Keyfr("https://example.org");
    delay(200);
    Key("entree");

    // Attend le chargement de la page
    delay(15000);

    // Ferme la fenêtre active
    Keyspecial("fermer");

    Keyboard.end();
  }
}
