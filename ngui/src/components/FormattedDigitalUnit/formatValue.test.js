import { getConvertedValueAndUnitName, IEC_UNITS, SI_UNITS } from "./FormattedDigitalUnit";

describe("Testing SI", () => {
  const convertInSi = (value, baseSize) => getConvertedValueAndUnitName(value, baseSize);

  describe("Converting bytes", () => {
    const convert = (value) => convertInSi(value, SI_UNITS.BYTE);

    test("0 should be 0 bytes", () => {
      expect(convert(0)).toEqual([0, SI_UNITS.BYTE]);
    });
    test("0.5 should be 0.5 bytes", () => {
      expect(convert(0.5)).toEqual([0.5, SI_UNITS.BYTE]);
    });
    test("999 should be 999 bytes", () => {
      expect(convert(999)).toEqual([999, SI_UNITS.BYTE]);
    });
    test("1000 should be 1 kilobyte", () => {
      expect(convert(1000)).toEqual([1, SI_UNITS.KILOBYTE]);
    });
    test("312312312 should be 312312312 megabytes", () => {
      expect(convert(312312312)).toEqual([312.312312, SI_UNITS.MEGABYTE]);
    });
  });

  describe("Converting megabytes", () => {
    const convert = (value) => convertInSi(value, SI_UNITS.MEGABYTE);

    test("0 should be 0 megabyte", () => {
      expect(convert(0)).toEqual([0, SI_UNITS.MEGABYTE]);
    });
    test("0.5 should be 0.5 megabyte", () => {
      expect(convert(0.5)).toEqual([0.5, SI_UNITS.MEGABYTE]);
    });
    test("999 should be 999 megabytes", () => {
      expect(convert(999)).toEqual([999, SI_UNITS.MEGABYTE]);
    });
    test("1000 should be 1 gigabyte", () => {
      expect(convert(1000)).toEqual([1, SI_UNITS.GIGABYTE]);
    });
    test("13213 should be 13.213 gigabyte", () => {
      expect(convert(13213)).toEqual([13.213, SI_UNITS.GIGABYTE]);
    });
    test("312312312 should be 312.312312 terabytes", () => {
      expect(convert(312312312)).toEqual([312.312312, SI_UNITS.TERABYTE]);
    });
  });

  describe("Converting petabytes", () => {
    const convert = (value) => convertInSi(value, SI_UNITS.PETABYTE);

    test("0 should be 0 petabyte", () => {
      expect(convert(0)).toEqual([0, SI_UNITS.PETABYTE]);
    });
    test("0.5 should be 0.5 petabyte", () => {
      expect(convert(0.5)).toEqual([0.5, SI_UNITS.PETABYTE]);
    });
    test("999 should be 999 petabyte", () => {
      expect(convert(999)).toEqual([999, SI_UNITS.PETABYTE]);
    });

    describe("should be petabytes if value >= 1000", () => {
      test("1000 should be 1000 petabytes", () => {
        expect(convert(1000)).toEqual([1000, SI_UNITS.PETABYTE]);
      });
      test("1572864 should be 1572864 petabytes", () => {
        expect(convert(1572864)).toEqual([1572864, SI_UNITS.PETABYTE]);
      });
    });
  });
});

describe("Testing ISO/IEC 80000 ", () => {
  const convertInIec = (value, baseSize) => getConvertedValueAndUnitName(value, baseSize);

  describe("Converting bytes", () => {
    const convert = (value) => convertInIec(value, IEC_UNITS.BYTE);

    test("0 should be 0 bytes", () => {
      expect(convert(0)).toEqual([0, IEC_UNITS.BYTE]);
    });
    test("0.5 should be 0.5 bytes", () => {
      expect(convert(0.5)).toEqual([0.5, IEC_UNITS.BYTE]);
    });
    test("1023 should be 1023 bytes", () => {
      expect(convert(1023)).toEqual([1023, IEC_UNITS.BYTE]);
    });
    test("1024 should be 1 kibibytes", () => {
      expect(convert(1024)).toEqual([1, IEC_UNITS.KIBIBYTE]);
    });
    test("312312312 should be 297.84423065185547 mebibytes", () => {
      expect(convert(312312312)).toEqual([297.84423065185547, IEC_UNITS.MEBIBYTE]);
    });
  });

  describe("Converting megabytes", () => {
    const convert = (value) => convertInIec(value, IEC_UNITS.MEBIBYTE);

    test("0 should be 0 mebibytes", () => {
      expect(convert(0)).toEqual([0, IEC_UNITS.MEBIBYTE]);
    });
    test("0.5 should be 0.5 mebibytes", () => {
      expect(convert(0.5)).toEqual([0.5, IEC_UNITS.MEBIBYTE]);
    });
    test("1023 should be 1023 mebibytes", () => {
      expect(convert(1023)).toEqual([1023, IEC_UNITS.MEBIBYTE]);
    });
    test("1024 should be 1 gibibytes", () => {
      expect(convert(1024)).toEqual([1, IEC_UNITS.GIBIBYTE]);
    });
    test("312312312 should be 297.84423065185547 tebibytes", () => {
      expect(convert(312312312)).toEqual([297.84423065185547, IEC_UNITS.TEBIBYTE]);
    });
  });

  describe("Converting pebibtytes", () => {
    const convert = (value) => convertInIec(value, IEC_UNITS.PEBIBYTE);

    test("0 should be 0 pebibtytes", () => {
      expect(convert(0)).toEqual([0, IEC_UNITS.PEBIBYTE]);
    });
    test("0.5 should be 0.5 pebibtytes", () => {
      expect(convert(0.5)).toEqual([0.5, IEC_UNITS.PEBIBYTE]);
    });
    test("1023 should be 1023 pebibtytes", () => {
      expect(convert(1023)).toEqual([1023, IEC_UNITS.PEBIBYTE]);
    });

    describe("should be pebibtytes if value >= 1024", () => {
      test("1024 should be 1024 pebibtytes", () => {
        expect(convert(1024)).toEqual([1024, IEC_UNITS.PEBIBYTE]);
      });
      test("1572864 should be 1572864 pebibtytes", () => {
        expect(convert(1572864)).toEqual([1572864, IEC_UNITS.PEBIBYTE]);
      });
    });
  });
});
