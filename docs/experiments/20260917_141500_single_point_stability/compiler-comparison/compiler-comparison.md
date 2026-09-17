# Compiler comparison (zero-call)

C0 是归档中的已编译计划；C1 是全概念 AND 加所有两两 AND 的影子池。
C1 不使用 `importance` 进行选池，不新增词项，也没有应用数据库语法适配。

## P4

- C0 unique expressions: 2; C1: 16.
- Only C0: `C1 OR C2 OR C3 OR C4`.
- Only C1: `C1 AND C2 AND C3 AND C4 AND C5 AND C6; C1 AND C3; C1 AND C4; C1 AND C5; C1 AND C6; C2 AND C3; C2 AND C4; C2 AND C5; C2 AND C6; C3 AND C4; C3 AND C5; C3 AND C6; C4 AND C5; C4 AND C6; C5 AND C6`.
- This establishes changed query opportunities only; it says nothing about live recall.

## P5

- C0 unique expressions: 2; C1: 16.
- Only C0: `C1 OR C2 OR C3 OR C4`.
- Only C1: `C1 AND C2 AND C3 AND C4 AND C5 AND C6; C1 AND C3; C1 AND C4; C1 AND C5; C1 AND C6; C2 AND C3; C2 AND C4; C2 AND C5; C2 AND C6; C3 AND C4; C3 AND C5; C3 AND C6; C4 AND C5; C4 AND C6; C5 AND C6`.
- This establishes changed query opportunities only; it says nothing about live recall.

## P6

- C0 unique expressions: 2; C1: 16.
- Only C0: `C1 OR C2 OR C3 OR C4`.
- Only C1: `C1 AND C2 AND C3 AND C4 AND C5 AND C6; C1 AND C3; C1 AND C4; C1 AND C5; C1 AND C6; C2 AND C3; C2 AND C4; C2 AND C5; C2 AND C6; C3 AND C4; C3 AND C5; C3 AND C6; C4 AND C5; C4 AND C6; C5 AND C6`.
- This establishes changed query opportunities only; it says nothing about live recall.
