from io import (
2
    BytesIO,
3
    StringIO,
4
)
5
import random
6
import string
7
​
8
import numpy as np
9
​
10
from pandas import (
11
    Categorical,
12
    DataFrame,
13
    concat,
14
    date_range,
15
    read_csv,
16
    to_datetime,
17
)
18
​
19
from ..pandas_vb_common import (
20
    BaseIO,
21
    tm,
22
)
23
​
24
​
25
class ToCSV(BaseIO):
26
    fname = "__test__.csv"
27
    params = ["wide", "long", "mixed"]
28
    param_names = ["kind"]
29
​
30
    def setup(self, kind):
31
        wide_frame = DataFrame(np.random.randn(3000, 30))
32
        long_frame = DataFrame(
33
            {
34
                "A": np.arange(50000),
35
                "B": np.arange(50000) + 1.0,
36
                "C": np.arange(50000) + 2.0,
37
                "D": np.arange(50000) + 3.0,
38
            }
39
        )
40
        mixed_frame = DataFrame(
41
            {
42
                "float": np.random.randn(5000),
43
                "int": np.random.randn(5000).astype(int),
44
                "bool": (np.arange(5000) % 2) == 0,
45
                "datetime": date_range("2001", freq="s", periods=5000),
46
                "object": ["foo"] * 5000,
47
            }
48
        )
49
        mixed_frame.loc[30:500, "float"] = np.nan
50
        data = {"wide": wide_frame, "long": long_frame, "mixed": mixed_frame}
51
        self.df = data[kind]
52
​
53
    def time_frame(self, kind):
54
        self.df.to_csv(self.fname)
55
​
56
​
57
class ToCSVMultiIndexUnusedLevels(BaseIO):
58
    fname = "__test__.csv"
59
​
60
    def setup(self):
61
        df = DataFrame({"a": np.random.randn(100_000), "b": 1, "c": 1})
62
        self.df = df.set_index(["a", "b"])
63
        self.df_unused_levels = self.df.iloc[:10_000]
64
        self.df_single_index = df.set_index(["a"]).iloc[:10_000]
65
​
66
    def time_full_frame(self):
67
        self.df.to_csv(self.fname)
68
​
69
    def time_sliced_frame(self):
70
        self.df_unused_levels.to_csv(self.fname)
71
​
72
    def time_single_index_frame(self):
73
        self.df_single_index.to_csv(self.fname)
74
​
75
​
76
class ToCSVDatetime(BaseIO):
77
    fname = "__test__.csv"
78
​
79
    def setup(self):
80
        rng = date_range("1/1/2000", periods=1000)
81
        self.data = DataFrame(rng, index=rng)
82
​
83
    def time_frame_date_formatting(self):
84
        self.data.to_csv(self.fname, date_format="%Y%m%d")
85
​
86
​
87
class ToCSVDatetimeIndex(BaseIO):
88
    fname = "__test__.csv"
89
​
90
    def setup(self):
91
        rng = date_range("2000", periods=100_000, freq="S")
92
        self.data = DataFrame({"a": 1}, index=rng)
93
​
94
    def time_frame_date_formatting_index(self):
95
        self.data.to_csv(self.fname, date_format="%Y-%m-%d %H:%M:%S")
96
​
97
    def time_frame_date_no_format_index(self):
98
        self.data.to_csv(self.fname)
99
​
100
​
101
class ToCSVDatetimeBig(BaseIO):
102
    fname = "__test__.csv"
103
    timeout = 1500
104
    params = [1000, 10000, 100000]
105
    param_names = ["obs"]
106
​
107
    def setup(self, obs):
108
        d = "2018-11-29"
109
        dt = "2018-11-26 11:18:27.0"
110
        self.data = DataFrame(
111
            {
112
                "dt": [np.datetime64(dt)] * obs,
113
                "d": [np.datetime64(d)] * obs,
114
                "r": [np.random.uniform()] * obs,
115
            }
116
        )
117
​
118
    def time_frame(self, obs):
119
        self.data.to_csv(self.fname)
120
​
121
​
122
class ToCSVIndexes(BaseIO):
123
    fname = "__test__.csv"
124
​
125
    @staticmethod
126
    def _create_df(rows, cols):
127
        index_cols = {
128
            "index1": np.random.randint(0, rows, rows),
129
            "index2": np.full(rows, 1, dtype=int),
130
            "index3": np.full(rows, 1, dtype=int),
131
        }
132
        data_cols = {
133
            f"col{i}": np.random.uniform(0, 100000.0, rows) for i in range(cols)
134
        }
135
        df = DataFrame({**index_cols, **data_cols})
136
        return df
137
​
138
    def setup(self):
139
        ROWS = 100000
140
        COLS = 5
141
        # For tests using .head(), create an initial dataframe with this many times
142
        # more rows
143
        HEAD_ROW_MULTIPLIER = 10
144
​
145
        self.df_standard_index = self._create_df(ROWS, COLS)
146
​
147
        self.df_custom_index_then_head = (
148
            self._create_df(ROWS * HEAD_ROW_MULTIPLIER, COLS)
149
            .set_index(["index1", "index2", "index3"])
150
            .head(ROWS)
151
        )
152
​
153
        self.df_head_then_custom_index = (
154
            self._create_df(ROWS * HEAD_ROW_MULTIPLIER, COLS)
155
            .head(ROWS)
156
            .set_index(["index1", "index2", "index3"])
157
        )
158
​
159
    def time_standard_index(self):
160
        self.df_standard_index.to_csv(self.fname)
161
​
162
    def time_multiindex(self):
163
        self.df_head_then_custom_index.to_csv(self.fname)
164
​
165
    def time_head_of_multiindex(self):
166
        self.df_custom_index_then_head.to_csv(self.fname)
167
​
168
​
169
class StringIORewind:
170
    def data(self, stringio_object):
171
        stringio_object.seek(0)
172
        return stringio_object
173
​
174
​
175
class ReadCSVDInferDatetimeFormat(StringIORewind):
176
    params = ([True, False], ["custom", "iso8601", "ymd"])
177
    param_names = ["infer_datetime_format", "format"]
178
​
179
    def setup(self, infer_datetime_format, format):
180
        rng = date_range("1/1/2000", periods=1000)
181
        formats = {
182
            "custom": "%m/%d/%Y %H:%M:%S.%f",
183
            "iso8601": "%Y-%m-%d %H:%M:%S",
184
            "ymd": "%Y%m%d",
185
        }
186
        dt_format = formats[format]
187
        self.StringIO_input = StringIO("\n".join(rng.strftime(dt_format).tolist()))
188
​
189
    def time_read_csv(self, infer_datetime_format, format):
190
        read_csv(
191
            self.data(self.StringIO_input),
192
            header=None,
193
            names=["foo"],
194
            parse_dates=["foo"],
195
            infer_datetime_format=infer_datetime_format,
196
        )
197
​
198
​
199
class ReadCSVConcatDatetime(StringIORewind):
200
    iso8601 = "%Y-%m-%d %H:%M:%S"
201
​
202
    def setup(self):
203
        rng = date_range("1/1/2000", periods=50000, freq="S")
204
        self.StringIO_input = StringIO("\n".join(rng.strftime(self.iso8601).tolist()))
205
​
206
    def time_read_csv(self):
207
        read_csv(
208
            self.data(self.StringIO_input),
209
            header=None,
210
            names=["foo"],
211
            parse_dates=["foo"],
212
            infer_datetime_format=False,
213
        )
214
​
215
​
216
class ReadCSVConcatDatetimeBadDateValue(StringIORewind):
217
    params = (["nan", "0", ""],)
218
    param_names = ["bad_date_value"]
219
​
220
    def setup(self, bad_date_value):
221
        self.StringIO_input = StringIO((f"{bad_date_value},\n") * 50000)
222
​
223
    def time_read_csv(self, bad_date_value):
224
        read_csv(
225
            self.data(self.StringIO_input),
226
            header=None,
227
            names=["foo", "bar"],
228
            parse_dates=["foo"],
229
            infer_datetime_format=False,
230
        )
231
​
232
​
233
class ReadCSVSkipRows(BaseIO):
234
    fname = "__test__.csv"
235
    params = ([None, 10000], ["c", "python", "pyarrow"])
236
    param_names = ["skiprows", "engine"]
237
​
238
    def setup(self, skiprows, engine):
239
        N = 20000
240
        index = tm.makeStringIndex(N)
241
        df = DataFrame(
242
            {
243
                "float1": np.random.randn(N),
244
                "float2": np.random.randn(N),
245
                "string1": ["foo"] * N,
246
                "bool1": [True] * N,
247
                "int1": np.random.randint(0, N, size=N),
248
            },
249
            index=index,
250
        )
251
        df.to_csv(self.fname)
252
​
253
    def time_skipprows(self, skiprows, engine):
254
        read_csv(self.fname, skiprows=skiprows, engine=engine)
255
​
256
​
257
class ReadUint64Integers(StringIORewind):
258
    def setup(self):
259
        self.na_values = [2**63 + 500]
260
        arr = np.arange(10000).astype("uint64") + 2**63
261
        self.data1 = StringIO("\n".join(arr.astype(str).tolist()))
262
        arr = arr.astype(object)
263
        arr[500] = -1
264
        self.data2 = StringIO("\n".join(arr.astype(str).tolist()))
265
​
266
    def time_read_uint64(self):
267
        read_csv(self.data(self.data1), header=None, names=["foo"])
268
​
269
    def time_read_uint64_neg_values(self):
270
        read_csv(self.data(self.data2), header=None, names=["foo"])
271
​
272
    def time_read_uint64_na_values(self):
273
        read_csv(
274
            self.data(self.data1), header=None, names=["foo"], na_values=self.na_values
275
        )
276
​
277
​
278
class ReadCSVThousands(BaseIO):
279
    fname = "__test__.csv"
280
    params = ([",", "|"], [None, ","], ["c", "python"])
281
    param_names = ["sep", "thousands", "engine"]
282
​
283
    def setup(self, sep, thousands, engine):
284
        N = 10000
285
        K = 8
286
        data = np.random.randn(N, K) * np.random.randint(100, 10000, (N, K))
287
        df = DataFrame(data)
288
        if thousands is not None:
289
            fmt = f":{thousands}"
290
            fmt = "{" + fmt + "}"
291
            df = df.applymap(lambda x: fmt.format(x))
292
        df.to_csv(self.fname, sep=sep)
293
​
294
    def time_thousands(self, sep, thousands, engine):
295
        read_csv(self.fname, sep=sep, thousands=thousands, engine=engine)
296
​
297
​
298
class ReadCSVComment(StringIORewind):
299
    params = ["c", "python"]
300
    param_names = ["engine"]
301
​
302
    def setup(self, engine):
303
        data = ["A,B,C"] + (["1,2,3 # comment"] * 100000)
304
        self.StringIO_input = StringIO("\n".join(data))
305
​
306
    def time_comment(self, engine):
307
        read_csv(
308
            self.data(self.StringIO_input), comment="#", header=None, names=list("abc")
309
        )
310
​
311
​
312
class ReadCSVFloatPrecision(StringIORewind):
313
    params = ([",", ";"], [".", "_"], [None, "high", "round_trip"])
314
    param_names = ["sep", "decimal", "float_precision"]
315
​
316
    def setup(self, sep, decimal, float_precision):
317
        floats = [
318
            "".join([random.choice(string.digits) for _ in range(28)])
319
            for _ in range(15)
320
        ]
321
        rows = sep.join([f"0{decimal}{{}}"] * 3) + "\n"
322
        data = rows * 5
323
        data = data.format(*floats) * 200  # 1000 x 3 strings csv
324
        self.StringIO_input = StringIO(data)
325
​
326
    def time_read_csv(self, sep, decimal, float_precision):
327
        read_csv(
328
            self.data(self.StringIO_input),
329
            sep=sep,
330
            header=None,
331
            names=list("abc"),
332
            float_precision=float_precision,
333
        )
334
​
335
    def time_read_csv_python_engine(self, sep, decimal, float_precision):
336
        read_csv(
337
            self.data(self.StringIO_input),
338
            sep=sep,
339
            header=None,
340
            engine="python",
341
            float_precision=None,
342
            names=list("abc"),
343
        )
344
​
345
​
346
class ReadCSVEngine(StringIORewind):
347
    params = ["c", "python", "pyarrow"]
348
    param_names = ["engine"]
349
​
350
    def setup(self, engine):
351
        data = ["A,B,C,D,E"] + (["1,2,3,4,5"] * 100000)
352
        self.StringIO_input = StringIO("\n".join(data))
353
        # simulate reading from file
354
        self.BytesIO_input = BytesIO(self.StringIO_input.read().encode("utf-8"))
355
​
356
    def time_read_stringcsv(self, engine):
357
        read_csv(self.data(self.StringIO_input), engine=engine)
358
​
359
    def time_read_bytescsv(self, engine):
360
        read_csv(self.data(self.BytesIO_input), engine=engine)
361
​
362
​
363
class ReadCSVCategorical(BaseIO):
364
    fname = "__test__.csv"
365
    params = ["c", "python"]
366
    param_names = ["engine"]
367
​
368
    def setup(self, engine):
369
        N = 100000
370
        group1 = ["aaaaaaaa", "bbbbbbb", "cccccccc", "dddddddd", "eeeeeeee"]
371
        df = DataFrame(np.random.choice(group1, (N, 3)), columns=list("abc"))
372
        df.to_csv(self.fname, index=False)
373
​
374
    def time_convert_post(self, engine):
375
        read_csv(self.fname, engine=engine).apply(Categorical)
376
​
377
    def time_convert_direct(self, engine):
378
        read_csv(self.fname, engine=engine, dtype="category")
379
​
380
​
381
class ReadCSVParseDates(StringIORewind):
382
    params = ["c", "python"]
383
    param_names = ["engine"]
384
​
385
    def setup(self, engine):
386
        data = """{},19:00:00,18:56:00,0.8100,2.8100,7.2000,0.0000,280.0000\n
387
                  {},20:00:00,19:56:00,0.0100,2.2100,7.2000,0.0000,260.0000\n
388
                  {},21:00:00,20:56:00,-0.5900,2.2100,5.7000,0.0000,280.0000\n
389
                  {},21:00:00,21:18:00,-0.9900,2.0100,3.6000,0.0000,270.0000\n
390
                  {},22:00:00,21:56:00,-0.5900,1.7100,5.1000,0.0000,290.0000\n
391
               """
392
        two_cols = ["KORD,19990127"] * 5
393
        data = data.format(*two_cols)
394
        self.StringIO_input = StringIO(data)
395
​
396
    def time_multiple_date(self, engine):
397
        read_csv(
398
            self.data(self.StringIO_input),
399
            engine=engine,
400
            sep=",",
401
            header=None,
402
            names=list(string.digits[:9]),
403
            parse_dates=[[1, 2], [1, 3]],
404
        )
405
​
406
    def time_baseline(self, engine):
407
        read_csv(
408
            self.data(self.StringIO_input),
409
            engine=engine,
410
            sep=",",
411
            header=None,
412
            parse_dates=[1],
413
            names=list(string.digits[:9]),
414
        )
415
​
416
​
417
class ReadCSVCachedParseDates(StringIORewind):
418
    params = ([True, False], ["c", "python"])
419
    param_names = ["do_cache", "engine"]
420
​
421
    def setup(self, do_cache, engine):
422
        data = ("\n".join([f"10/{year}" for year in range(2000, 2100)]) + "\n") * 10
423
        self.StringIO_input = StringIO(data)
424
​
425
    def time_read_csv_cached(self, do_cache, engine):
426
        try:
427
            read_csv(
428
                self.data(self.StringIO_input),
429
                engine=engine,
430
                header=None,
431
                parse_dates=[0],
432
                cache_dates=do_cache,
433
            )
434
        except TypeError:
435
            # cache_dates is a new keyword in 0.25
436
            pass
437
​
438
​
439
class ReadCSVMemoryGrowth(BaseIO):
440
    chunksize = 20
441
    num_rows = 1000
442
    fname = "__test__.csv"
443
    params = ["c", "python"]
444
    param_names = ["engine"]
445
​
446
    def setup(self, engine):
447
        with open(self.fname, "w") as f:
448
            for i in range(self.num_rows):
449
                f.write(f"{i}\n")
450
​
451
    def mem_parser_chunks(self, engine):
452
        # see gh-24805.
453
        result = read_csv(self.fname, chunksize=self.chunksize, engine=engine)
454
​
455
        for _ in result:
456
            pass
457
​
458
​
459
class ReadCSVParseSpecialDate(StringIORewind):
460
    params = (["mY", "mdY", "hm"], ["c", "python"])
461
    param_names = ["value", "engine"]
462
    objects = {
463
        "mY": "01-2019\n10-2019\n02/2000\n",
464
        "mdY": "12/02/2010\n",
465
        "hm": "21:34\n",
466
    }
467
​
468
    def setup(self, value, engine):
469
        count_elem = 10000
470
        data = self.objects[value] * count_elem
471
        self.StringIO_input = StringIO(data)
472
​
473
    def time_read_special_date(self, value, engine):
474
        read_csv(
475
            self.data(self.StringIO_input),
476
            engine=engine,
477
            sep=",",
478
            header=None,
479
            names=["Date"],
480
            parse_dates=["Date"],
481
        )
482
​
483
​
484
class ReadCSVMemMapUTF8:
485
    fname = "__test__.csv"
486
    number = 5
487
​
488
    def setup(self):
489
        lines = []
490
        line_length = 128
491
        start_char = " "
492
        end_char = "\U00010080"
493
        # This for loop creates a list of 128-char strings
494
        # consisting of consecutive Unicode chars
495
        for lnum in range(ord(start_char), ord(end_char), line_length):
496
            line = "".join([chr(c) for c in range(lnum, lnum + 0x80)]) + "\n"
497
            try:
498
                line.encode("utf-8")
499
            except UnicodeEncodeError:
500
                # Some 16-bit words are not valid Unicode chars and must be skipped
501
                continue
502
            lines.append(line)
503
        df = DataFrame(lines)
504
        df = concat([df for n in range(100)], ignore_index=True)
505
        df.to_csv(self.fname, index=False, header=False, encoding="utf-8")
506
​
507
    def time_read_memmapped_utf8(self):
508
        read_csv(self.fname, header=None, memory_map=True, encoding="utf-8", engine="c")
509
​
510
​
511
class ParseDateComparison(StringIORewind):
512
    params = ([False, True],)
513
    param_names = ["cache_dates"]
514
​
515
    def setup(self, cache_dates):
516
        count_elem = 10000
517
        data = "12-02-2010\n" * count_elem
518
        self.StringIO_input = StringIO(data)
519
​
520
    def time_read_csv_dayfirst(self, cache_dates):
521
        try:
522
            read_csv(
523
                self.data(self.StringIO_input),
524
                sep=",",
525
                header=None,
526
                names=["Date"],
527
                parse_dates=["Date"],
528
                cache_dates=cache_dates,
529
                dayfirst=True,
530
            )
531
        except TypeError:
532
            # cache_dates is a new keyword in 0.25
533
            pass
534
​
535
    def time_to_datetime_dayfirst(self, cache_dates):
536
        df = read_csv(
537
            self.data(self.StringIO_input), dtype={"date": str}, names=["date"]
538
        )
539
        to_datetime(df["date"], cache=cache_dates, dayfirst=True)
540
​
541
    def time_to_datetime_format_DD_MM_YYYY(self, cache_dates):
542
        df = read_csv(
543
            self.data(self.StringIO_input), dtype={"date": str}, names=["date"]
544
        )
545
        to_datetime(df["date"], cache=cache_dates, format="%d-%m-%Y")
546
​
547
​
548
class ReadCSVIndexCol(StringIORewind):
549
    def setup(self):
550
        count_elem = 100_000
551
        data = "a,b\n" + "1,2\n" * count_elem
552
        self.StringIO_input = StringIO(data)
553
​
554
    def time_read_csv_index_col(self):
555
        read_csv(self.StringIO_input, index_col="a")
556
​
557
​
558
from ..pandas_vb_common import setup  # noqa: F401 isort:skip
Source: https://github.com/pandas-dev/pandas/blob/main/asv_bench/benchmarks/io/csv.py