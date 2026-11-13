# Chytré monitorování skleníku

> Semestrální projekt předmětu Digitální elektronika 2

## Členové týmu

- **Daniel Bačovčin**
- **Jan Rozík**

## Cíl projektu

Cílem projektu je vytvořit vestavěný systém na platformě **Raspberry Pi Pico W** na rozšiřující vývojové desce DFRobot Gravity: Expansion Board v jazyce **MicroPython** pro automatické sledování a regulaci mikroklimatu ve skleníku. Systém průběžně měří teplotu, relativní vlhkost vzduchu a vlhkost půdy a naměřené hodnoty zobrazuje na OLED displeji.

Uživatel může pomocí rotačního enkodéru v rozhraní nastavovat ideální cílové hodnoty všech tří veličin. Při překročení nastavených mezí o definovanou odchylku systém automaticky sepne odvětrávací ventilátor přes relé modul. Prostřednictvím RGB LED se vizuálně signalizuje aktuální „nálada“ rostlin vypočítaná ze změřených parametrů.

<img width="2811" height="1677" alt="obrazek" src="https://github.com/user-attachments/assets/a78e1c5d-67d6-467c-9ea8-389fb597305d" />

## Vstupní moduly

### BME280 
* Integrovaný digitální senzor měřící teplotu, relativní vlhkost vzduchu a barometrický tlak.
* Modul pracuje s napájecím napětím 3,3 V a komunikuje po sběrnici I2C.
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

| Pin modulu | Odpovídající pin mikrokontroléru| Funkce |
| :---: | :---: | :---: |
| `VCC` | `3V3(OUT)` | Napájení modulu|
| `GND` | `GND` | Společná zem |
| `AOUT` | `GP28` | Analogový výstupní signál (ADC2) |

### Rotační enkodér (KY-040)
* Rotační enkodér s neomezeným úhlem otáčení, mechanickou aretací kroků a integrovaným spínacím tlačítkem v ose hřídele.
* Při otáčení modul generuje přes piny `CLK` a `DT` dva fázově posunuté obdélníkové signály. Podle pořadí náběžných/sestupných je možné určit směr otáčení.
* Slouží jako hlavní ovládací prvek uživatelského rozhraní. Dlouhým stiskem tlačítka se volí mezi módem zobrazení a modém nastavovaní ideálních podmínek ve skleníku. Ty se nastavují otačením. 

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

