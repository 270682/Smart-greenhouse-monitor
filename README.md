# Chytré monitorování skleníku

> Semestrální projekt předmětu Digitální elektronika 2

## Členové týmu

- **Daniel Bačovčin**: HW design, SW design 
- **Jan Rozík**: HW desing, SW design, dokumentace

## Cíl projektu

Cílem projektu je vytvořit vestavěný systém na platformě **Raspberry Pi Pico W** na rozšiřující vývojové desce DFRobot Gravity: Expansion Board v jazyce **MicroPython** (v1.29.0) pro automatické sledování a regulaci mikroklimatu ve skleníku. Systém průběžně měří teplotu, relativní vlhkost vzduchu a vlhkost půdy a naměřené hodnoty zobrazuje na OLED displeji.

Uživatel může pomocí rotačního enkodéru v rozhraní nastavovat ideální cílové hodnoty všech tří veličin. Při překročení nastavených mezí o definovanou odchylku systém automaticky sepne odvětrávací ventilátor přes relé modul. Prostřednictvím RGB LED se vizuálně signalizuje aktuální „nálada“ rostlin vypočítaná ze změřených parametrů.

<img width="2869" height="1733" alt="obrazek" src="https://github.com/user-attachments/assets/f844f850-31c6-4a97-8dba-ec76d1d7c3b1" />

## Vstupní moduly

### BME280 
* Integrovaný digitální senzor měřící teplotu, relativní vlhkost vzduchu a barometrický tlak.
* Modul pracuje s napájecím napětím 3,3 V a komunikuje po sběrnici I2C1.
* Průběžně snímá mikroklima (teplotu a relativní vlhkost vzduchu) uvnitř skleníku.

| Pin modulu | Odpovídající pin mikrokontroléru| Funkce |
| :---: | :---: | :---: |
| `VCC` | `3V3 (OUT)` | Napájení modulu |
| `GND` | `GND` | Společná zem |
| `SDA` | `GP26` | Datová linka sběrnice I2C1 |
| `SCL` | `GP27` | Hodinový signál sběrnice I2C1 |

### Senzor vlhkosti půdy
* Kapacitní čidlo vlhkosti substrátu s analogovým napěťovým výstupem (`AOUT`) a napájením 3,3 V.
* Naměřená kapacita je převedena na spojité analogové napětí (čím vyšší vlhkost, tím nižší výstupní napětí), které je mikrokontrolérem převedeno na digitální hodnotu pomocí 12bitového ADC převodníku.
* Sleduje stav závlahy substrátu. Uživatel je při poklesu upozorněň na zalití.
* [Odkaz](https://wokwi.com/projects/481414252056190977) na simulaci v online programu Wokwi s testem použitého ovladače 
 

| Pin modulu | Odpovídající pin mikrokontroléru| Funkce |
| :---: | :---: | :---: |
| `VCC` | `3V3(OUT)` | Napájení modulu|
| `GND` | `GND` | Společná zem |
| `AOUT` | `GP28` | Analogový výstupní signál (ADC2) |

### Rotační enkodér (KY-040)
* Rotační enkodér s neomezeným úhlem otáčení, mechanickou aretací kroků a integrovaným spínacím tlačítkem v ose hřídele.
* Při otáčení modul generuje přes piny `CLK` a `DT` dva fázově posunuté obdélníkové signály. Podle pořadí náběžných/sestupných je možné určit směr otáčení.
* Slouží jako hlavní ovládací prvek uživatelského rozhraní. Dlouhým stiskem tlačítka se volí mezi módem zobrazení a modém nastavovaní ideálních podmínek ve skleníku. Ty se nastavují otačením.
* [Odkaz](https://wokwi.com/projects/481477403419581441) na simulaci v online programu Wokwi s testem použitého ovladače.

| Pin modulu | Odpovídající pin mikrokontroléru | Funkce |
| :---: | :---: | :---: |
| `CLK` | `GP13` | Výstupní pulzní signál |
| `DT` | `GP14` | Výstupní pulzní signál |
| `SW` | `GP15` | Integrované tlačítko |
| `+` | `3V3(OUT)` | Napájení |
| `GND` | `GND` | Společná zem |

### Tlačítko 
* Jednoduchý mikrospínač 
* Slouží k manuálnímu zapínání a vypínání OLED displeje

| Pin modulu | Odpovídající pin mikrokontroléru | Funkce |
| :---: | :---: | :---: |
| `4` | `GP17` | Digitální vstup s interním `PULL_UP` rezistorem |
| `2` | `GND` | Společná zem |

## Výstupní moduly

### OLED displej SH1106
* Monochromatický 1.3" displej s rozlišením 128 × 64 pixelů.
* Komunikace přes sběrnici I2C0.
* Zobrazuje aktuálně naměřenou teplotu, relativní vlhkost vzduchu a vlhkost půdy. Při překročení limitních hodnot zobrazí upozornění.
* [Odkaz](https://wokwi.com/projects/481403513555412993) na simulaci v online programu Wokwi s testem použitého ovladače 

| Pin modulu | Odpovídající pin mikrokontroléru | Funkce |
| :---: | :---: | :---: |
| `VCC` | `3V3(OUT)` | Napájení displeje (3,3 V) |
| `GND` | `GND` | Společná zem |
| `SDA` | `GP4` | Datová linka sběrnice I2C0 |
| `SCK` | `GP5` | Hodinový signál sběrnice I2C0 |

### Ventilátor 
* Malý stejnosměrný ventilátor s napájecím napětím 12 V.
* Zajišťuje odvětrávání skleníku při překročení nastavené horní meze teploty nebo relativní vlhkosti vzduchu.

| Pin modulu | Připojení | Funkce |
| :---: | :---: | :---: |
| `VCC (+)` | `NO` (+12 V) | Napájení |
| `GND` | `GND` | Společná zem |

### Relé modul 
* Výkonový spínací prvek ventilátoru
* Při sepnutí posílá na ventilátor napětí 12 V z externího zdroje
* Řídíci vstup je opticky oddělen
* [Odkaz](https://wokwi.com/projects/481421928680142849) na simulaci v online programu Wokwi s testem použitého ovladače 


| Pin modulu | Připojení | Funkce |
| :---: | :---: | :---: |
| `VCC` | `VBUS` (+5 V) | Napájení |
| `GND` | `GND` | Společná zem |
| `IN` | `GP16` | Řídicí vstup |
| `NO` | `V-ext` (+12 V) |  |
| `COM` | `Ventilátor (+)` |  |

### RGB LED (NeoPixel)
* Adresovatelná RGB LED s integrovaným řídicím čipem WS2812.
* Mikrokontrolér posílá po datovém pinu bitový tok s informací o intenzitě jednotlivých složek (24 bitů pro složky G, R, B - tj. 8 bitů pro jednu složku). Integrovaný řadič pomocí PWM modulace nastaví jas jednotlivých složek.
* Poskytuje vizuální indikaci celkového stavu („nálady“) rostlin ve skleníku
* [Odkaz](https://wokwi.com/projects/481478909512718337) na simulaci v online programu Wokwi s testem použitého ovladače 

| Pin modulu | Pin na Pico W | Funkce |
| :---: | :---: | :---: |
| `5V` | `3V3(OUT)` | Napájení LED modulu |
| `DIN` | `GP22` | Datový vstup |
| `GND` | `GND` | Společná zem |

| Barva LED | RGB hodnota | Nálada rostlin |
| :---: | :---: | :---: |
| **Fialová** | `(220, 0, 255)` | Výpadek komunikace s některým čidlem |
| **Červená** | `(255, 0, 0)` | Vysoká teplota vzduchu |
| **Azurová** | `(0, 220, 255)` | Nízká teplota vzduchu |
| **Oranžová** | `(255, 90, 0)` | Suchá půda nebo vzduch |
| **Modrá** | `(0, 40, 255)` | Vlhkost půdy nebo vzduchu je nad horním limitem |
| **Zelená** | `(0, 255, 40)` | Optimální podmínky ve skleníku |

## Použité knihovny

| Knihovna / Modul | Zdroj |
| :---: | :---: |
| `sh1106.py` | Výukové materiály předmětu ([micropython-course-labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs) |
| `bme280.py` | Výukové materiály předmětu ([micropython-course-labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs) |
| `adc_read.py` | Výukové materiály předmětu ([micropython-course-labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs) |
| `gpio_devices.py` | Výukové materiály předmětu ([micropython-course-labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs) |
| `oled_driver.py` | Vlastní implementace (metody `draw_bar()` a `draw_measurement()` převzaty z [micropython-course-labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs)) |
| `soil_moisture_driver.py` | Vlastní implementace |
| `relay_driver.py` | Vlastní implementace |
| `led_driver.py` | Vlastní implementace |
| `rotary_encoder.py` | Vlastní implementace |


