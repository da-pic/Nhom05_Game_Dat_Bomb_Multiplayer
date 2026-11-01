# Vị trí trong báo cáo cũ cần đối chiếu khi cập nhật recovery

Sinh từ khảo sát ngày 27/10/2026; **147 dòng ứng viên**, không phải 147 lỗi.
Các câu về phục hồi baseline, số liệu lịch sử hoặc giới hạn vẫn có thể đúng. Đọc cả tiểu mục trước khi sửa.
Số dòng/heading ở đây thuộc các chương trước cập nhật; sẽ thay đổi khi biên tập các nhiệm vụ sau.

Đối chiếu kế hoạch và phân loại thủ công tại [hồ sơ nhiệm vụ 1](01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).

## 02_TOM_TAT.md

- [Dòng 13](../chapters/02_TOM_TAT.md:13) — Lượt suite mới đạt 133/133 JUnit test; ba lượt reliability bổ sung đạt 84/84 lần thực thi test.

- [Dòng 16](../chapters/02_TOM_TAT.md:16) — Kết quả còn giới hạn ở fixture và loopback; chưa nghiệm thu GUI/LAN, soak dài hạn hoặc resume trận,

## 04_GIOI_THIEU.md

- [Dòng 29](../chapters/04_GIOI_THIEU.md:29) — phát hiện nền không khớp và phục hồi bằng full mà không áp lại effect gameplay.

- [Dòng 55](../chapters/04_GIOI_THIEU.md:55) — Phạm vi kết quả hiện tại chưa gồm nghiệm thu GUI/LAN nhiều máy, tải tối đa, soak dài hạn hoặc resume trận.

- [Dòng 56](../chapters/04_GIOI_THIEU.md:56) — Disconnect/leave được xử lý theo chính sách kết thúc lượt hiện hành.

## 05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md

- [Dòng 48](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:48) — Bản hiện hành chưa cung cấp chức năng reconnect để tiếp tục trận; có token hoặc API session

- [Dòng 209](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:209) — | Full snapshot | Tái dựng nền đầy đủ | Dữ liệu lặp lại; không phụ thuộc baseline delta | Khởi tạo và phục hồi |

## 06_DINH_NGHIA_BAI_TOAN.md

- [Dòng 43](../chapters/06_DINH_NGHIA_BAI_TOAN.md:43) — | Phục hồi đồng bộ | Yêu cầu full state khi replica cần đồng bộ lại | Client | Đúng match; tuân theo giới hạn tần suất và chính sách server |

- [Dòng 184](../chapters/06_DINH_NGHIA_BAI_TOAN.md:184) — rời/mất kết nối khi lượt chưa có kết quả chốt dùng `ABORTED`, không coi như một chiến thắng gameplay.

- [Dòng 212](../chapters/06_DINH_NGHIA_BAI_TOAN.md:212) — | FR10 | Đồng bộ full/delta và phục hồi | Có full khởi tạo; delta áp đúng baseline; sai baseline yêu cầu full; loại dữ liệu thuộc match cũ | TV2, TV4 |

- [Dòng 215](../chapters/06_DINH_NGHIA_BAI_TOAN.md:215) — | FR13 | Rời phòng, mất kết nối và dọn tài nguyên | Hủy lượt đang chơi theo chính sách; cập nhật phòng; dừng runtime/worker liên quan; phòng khác tiếp tục | TV1, TV2, TV4 |

- [Dòng 220](../chapters/06_DINH_NGHIA_BAI_TOAN.md:220) — Tương tự, có codec delta chưa đủ chứng minh FR10 khi chưa kiểm tra ghép replica và phục hồi.

- [Dòng 238](../chapters/06_DINH_NGHIA_BAI_TOAN.md:238) — | NFR07 | Vòng đời và phục hồi lỗi | Stop runtime giải phóng thread/tài nguyên liên quan; client chậm/lỗi được xử lý có kiểm soát; resync không cộng lại item/damage |

- [Dòng 284](../chapters/06_DINH_NGHIA_BAI_TOAN.md:284) — | A04 | Client có thể nhận dữ liệu muộn và chưa biết toàn bộ thay đổi mới nhất | Prediction có thể sai; kết quả server được ưu tiên; khi mất baseline phải phục hồi bằng full |

- [Dòng 291](../chapters/06_DINH_NGHIA_BAI_TOAN.md:291) — > **Phân công: TV3 ghép mục 6.5; TV1 xác nhận reconnect/phòng, TV2 đồng bộ, TV4 phạm vi triển khai và bằng chứng.**

- [Dòng 299](../chapters/06_DINH_NGHIA_BAI_TOAN.md:299) — - **Reconnect để tiếp tục trận:** mất kết nối hiện kết thúc/hủy lượt theo chính sách, không giữ ghế và trạng thái để người chơi quay lại tiếp tục.

- [Dòng 300](../chapters/06_DINH_NGHIA_BAI_TOAN.md:300) —   API/token hoặc đặc tả reconnect còn tồn tại không chứng minh đã có luồng end-to-end.

- [Dòng 315](../chapters/06_DINH_NGHIA_BAI_TOAN.md:315) — [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md).

## 07_GIAI_PHAP_DE_XUAT.md

- [Dòng 5](../chapters/07_GIAI_PHAP_DE_XUAT.md:5) — dữ liệu trạng thái được truyền dưới dạng full/delta với cơ chế phục hồi baseline.

- [Dòng 64](../chapters/07_GIAI_PHAP_DE_XUAT.md:64) — | Lặp lại dữ liệu map/entity không đổi | Delta theo baseline và full phục hồi | Dung lượng đồng bộ, phát sinh chi phí so sánh |

- [Dòng 88](../chapters/07_GIAI_PHAP_DE_XUAT.md:88) — Hiện tại mất kết nối khi đang chơi hủy lượt theo chính sách ABORTED nếu chưa có kết quả chốt;

- [Dòng 89](../chapters/07_GIAI_PHAP_DE_XUAT.md:89) — không đề xuất giả rằng token/grace đã tạo thành tính năng resume.

- [Dòng 92](../chapters/07_GIAI_PHAP_DE_XUAT.md:92) — khi có thành viên rời/mất kết nối. Nếu bổ sung reconnect sau này, cần thiết kế lại chính sách giữ world/ghế,

- [Dòng 144](../chapters/07_GIAI_PHAP_DE_XUAT.md:144) — Nhánh lifecycle mô tả API core hiện có, không khẳng định route reconnect đã bật ở ứng dụng.

- [Dòng 205](../chapters/07_GIAI_PHAP_DE_XUAT.md:205) — ## 7.5. State Delta Compression và phục hồi baseline

- [Dòng 337](../chapters/07_GIAI_PHAP_DE_XUAT.md:337) — Nếu writer một client thất bại, transport/lobby xử lý disconnect theo chính sách;

- [Dòng 340](../chapters/07_GIAI_PHAP_DE_XUAT.md:340) — ### 7.5.5. Ghép replica và phục hồi baseline

- [Dòng 421](../chapters/07_GIAI_PHAP_DE_XUAT.md:421) — Tính cả full đầu/định kỳ/phục hồi của chế độ delta; nếu đo toàn luồng, phải tính các notice/control theo cùng quy tắc ở cả hai chế độ.

- [Dòng 465](../chapters/07_GIAI_PHAP_DE_XUAT.md:465) — | Full đầu/định kỳ/yêu cầu/FINISHED | Tạo và phục hồi nền đồng bộ theo policy | Chi phí full, chưa có tự chọn loại theo size |

- [Dòng 469](../chapters/07_GIAI_PHAP_DE_XUAT.md:469) — | Queue/budget hữu hạn và đóng client lỗi | Giới hạn một số dạng backlog, không tiếp tục sai baseline | Disconnect có thể hủy lượt theo chính sách hiện hành |

## 08_KIEN_TRUC_HE_THONG.md

- [Dòng 113](../chapters/08_KIEN_TRUC_HE_THONG.md:113) — resume trận. Với ứng dụng hiện tại, callback mất kết nối đi qua tầng điều phối để hủy lượt đang chơi và bỏ ghế;

- [Dòng 114](../chapters/08_KIEN_TRUC_HE_THONG.md:114) — metadata phiên còn tồn tại trong khoảng chờ dọn không đồng nghĩa world/roster được giữ để reconnect.

- [Dòng 223](../chapters/08_KIEN_TRUC_HE_THONG.md:223) — như disconnect/hard drop. Chúng không phải một event bus chung và không chứng minh kiến trúc event sourcing.

- [Dòng 388](../chapters/08_KIEN_TRUC_HE_THONG.md:388) — Kết thúc hành chính hoặc mất kết nối dùng chính sách ABORTED nếu lượt chưa có kết quả chốt.

- [Dòng 402](../chapters/08_KIEN_TRUC_HE_THONG.md:402) — Các cơ chế chống dữ liệu cũ không tạo ra khả năng resume trận sau mất kết nối.

## 09_THIET_KE_GIAO_TIEP_MANG.md

- [Dòng 124](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:124) — | `0x0002` | CONNECT_ACK, S→C | `playerId:S`, `reconnectToken`, `serverVersion`, `protocolVersion:2`, `heartbeatIntervalMs:2000`, `heartbeatTimeoutMs:10000`, `reconnectGraceMs:15000` |

- [Dòng 127](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:127) — | `0x0042` | DISCONNECT, C→S | `reason:"USER_QUIT"`; handler hỗ trợ đóng phiên chủ động |

- [Dòng 136](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:136) — đóng cửa sổ đều phát DISCONNECT. Mất kết nối trong lượt chơi hiện kết thúc/hủy lượt và bỏ ghế;

- [Dòng 137](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:137) — metadata phiên có thể còn chờ dọn tối đa theo grace, không còn world để resume.

- [Dòng 141](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:141) — `RECONNECT=0x0043` và `NETWORK_LOST=0x0044` có trong PacketType/tài liệu, nhưng router sản phẩm chưa đăng ký handler.

- [Dòng 142](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:142) — Enum reason `RECONNECT` trong request resync cũng không chứng minh đã có reconnect end-to-end.

- [Dòng 143](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:143) — `PLAYER_DISCONNECTED=0x0032` còn dùng trong các API/nhánh hạ tầng; đường lobby hiện tại chủ yếu cập nhật bằng GAME_OVER

- [Dòng 144](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:144) — và ROOM_STATE, không có luồng thông báo player-disconnected trong trận giữ ghế để tiếp tục chơi.

- [Dòng 146](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:146) — Không đưa các schema reconnect dự kiến thành sequence đã triển khai. Sau handshake, type chưa có handler có thể trả

- [Dòng 151](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:151) — và [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md).

- [Dòng 190](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:190) — ### 9.4.1. Message movement và phục hồi

- [Dòng 199](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:199) — | `0x0034` | REQUEST_FULL_STATE, C→S | `lastAppliedTick>=-1,reason:COLD_START/BASELINE_MISMATCH/RECONNECT` |

- [Dòng 298](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:298) — ### 9.4.4. Request full và phục hồi baseline

- [Dòng 310](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:310) — Baseline chung theo runtime/room nên full phục hồi được phát cho cả roster, dù một client yêu cầu.

- [Dòng 313](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:313) — Không diễn giải resync như giao thức reconnect hoặc bảo đảm sửa được mọi payload hỏng.

- [Dòng 370](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:370) — Reason là LAST_ALIVE, ALL_DEAD, TIMEOUT hoặc ABORTED. Chỉ LAST_ALIVE có winnerPlayerId;

- [Dòng 371](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:371) — ABORTED không có người thắng và rankings rỗng. Lượt kết thúc bình thường có full FINISHED/result,

- [Dòng 427](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:427) — **Hình 9.2. Input sequence và nhánh phục hồi baseline. Nhóm tự vẽ từ code project.**

- [Dòng 520](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:520) — Nhánh host End/leave/disconnect bỏ phần full FINISHED nếu chưa có kết quả gameplay;

- [Dòng 521](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:521) — nó dừng runtime và gửi ABORTED. Socket đã mất không được bảo đảm nhận thông báo cuối;

- [Dòng 562](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:562) — | EOF, frame thiếu byte hoặc timeout I/O | Dọn captured connection; phiên đã handshake đi qua chính sách disconnect | Nếu đang chơi, lobby có thể hủy lượt |

- [Dòng 568](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:568) — | Writer đầy/ghi quá hạn | Đóng client đó và cleanup | Theo chính sách lobby, một disconnect có thể làm hủy cả lượt của phòng |

- [Dòng 594](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:594) — Protocol hiện không có receipt ACK riêng cho snapshot, không có ACK nghiệp vụ riêng cho mọi lệnh và chưa có reconnect resume.

## 10_TRIEN_KHAI_HE_THONG.md

- [Dòng 74](../chapters/10_TRIEN_KHAI_HE_THONG.md:74) — inject map/extension factory vào runtime manager và cài observer cho disconnect/hard drop.

- [Dòng 124](../chapters/10_TRIEN_KHAI_HE_THONG.md:124) — | `SessionManager` | `register`, `find`, `handleUnexpectedDisconnect`, `hardDrop`, `broadcastToRoom` | Map phiên, trạng thái disconnect/expiry và callback vòng đời |

- [Dòng 148](../chapters/10_TRIEN_KHAI_HE_THONG.md:148) — Đây là kiểm tra ownership của kết nối, chưa chứng minh đã có generation/reconnect resume hoàn chỉnh.

- [Dòng 185](../chapters/10_TRIEN_KHAI_HE_THONG.md:185) — | DISCONNECTED | Socket mất, metadata có thể chờ expiry | `handleUnexpectedDisconnect` |

- [Dòng 189](../chapters/10_TRIEN_KHAI_HE_THONG.md:189) — map timer disconnect và ScheduledThreadPoolExecutor cho expiry.

- [Dòng 190](../chapters/10_TRIEN_KHAI_HE_THONG.md:190) — `handleUnexpectedDisconnect` đánh dấu DISCONNECTED, đóng socket, gọi observer rồi lên lịch hard drop theo grace.

- [Dòng 194](../chapters/10_TRIEN_KHAI_HE_THONG.md:194) — Lobby kết thúc lượt/bỏ ghế ngay khi disconnect, nên session metadata còn 15 giây không có nghĩa phòng/world vẫn được giữ.

- [Dòng 195](../chapters/10_TRIEN_KHAI_HE_THONG.md:195) — `SessionManager.reconnect` là API legacy có token/attachSocket/restoreState;

- [Dòng 196](../chapters/10_TRIEN_KHAI_HE_THONG.md:196) — router sản phẩm chưa đăng ký RECONNECT và chương này không nhận API đó là tính năng resume đã hoàn thành.

- [Dòng 216](../chapters/10_TRIEN_KHAI_HE_THONG.md:216) — Khi nhận kết quả bình thường hoặc End/leave/disconnect, `endMatch` dừng runtime, reset session/room,

- [Dòng 227](../chapters/10_TRIEN_KHAI_HE_THONG.md:227) — không DISCONNECTED/CLOSED. Sau đó tạo CHAT JSON qua LobbyPacketCodec và gửi cho các session nhận hợp lệ.

- [Dòng 239](../chapters/10_TRIEN_KHAI_HE_THONG.md:239) — Phiên chưa handshake hết hạn bị hard drop; phiên đã handshake đi qua unexpected disconnect và callback lifecycle.

- [Dòng 303](../chapters/10_TRIEN_KHAI_HE_THONG.md:303) — `PlayerDisconnectedCommand`, `PlayerReconnectedCommand`.

- [Dòng 318](../chapters/10_TRIEN_KHAI_HE_THONG.md:318) — Command disconnect đóng băng movement và có thể xóa player theo cờ; reconnect mở đóng băng và yêu cầu full state.

- [Dòng 319](../chapters/10_TRIEN_KHAI_HE_THONG.md:319) — Đây là API core, không phải bằng chứng luồng reconnect lobby đã khôi phục được trận đang chơi.

- [Dòng 470](../chapters/10_TRIEN_KHAI_HE_THONG.md:470) — | `ReconciliationController` | Cập nhật world, phục hồi authoritative và replay | Không thực hiện visual smoothing |

- [Dòng 518](../chapters/10_TRIEN_KHAI_HE_THONG.md:518) — phục hồi vị trí/hướng/tốc độ/trạng thái sống authoritative rồi mô phỏng lại input còn chờ theo thứ tự sequence.

- [Dòng 591](../chapters/10_TRIEN_KHAI_HE_THONG.md:591) — Thất bại trả BombError cụ thể. BombGameplayExtension kiểm tra thêm trạng thái trận và player disconnected

- [Dòng 685](../chapters/10_TRIEN_KHAI_HE_THONG.md:685) — Lobby dừng runtime và phát GAME_OVER; trường hợp rời phòng/đóng trận khi chưa có outcome có thể tạo ABORTED.

- [Dòng 700](../chapters/10_TRIEN_KHAI_HE_THONG.md:700) — Đây không phải event log lưu trên đĩa hoặc cam kết replay sau reconnect.

- [Dòng 805](../chapters/10_TRIEN_KHAI_HE_THONG.md:805) — | `ClientNetwork` | Connect/send/listener/receive/disconnect/close | TCP client dùng chung, không tự điều khiển world/UI |

- [Dòng 837](../chapters/10_TRIEN_KHAI_HE_THONG.md:837) — [SessionHandlers](../../src/main/java/com/bombit/server/dispatch/SessionHandlers.java) đăng ký CONNECT/PING/DISCONNECT.

- [Dòng 839](../chapters/10_TRIEN_KHAI_HE_THONG.md:839) — `LobbyGameServer` đăng ký các type lobby/gameplay; RECONNECT/NETWORK_LOST không được đăng ký trong đường sản phẩm.

- [Dòng 863](../chapters/10_TRIEN_KHAI_HE_THONG.md:863) — `disconnect()` dừng trạng thái, đóng socket để đánh thức reader, dừng watchdog, interrupt/join reader có thời hạn rồi clear queue.

- [Dòng 864](../chapters/10_TRIEN_KHAI_HE_THONG.md:864) — `close()` còn xóa listener và callback disconnect. Kiểm tra captured socket giúp reader cũ không tự đóng một socket khác;

- [Dòng 865](../chapters/10_TRIEN_KHAI_HE_THONG.md:865) — khả năng bảo vệ đó không được giới thiệu thành reconnect resume trận đã hoàn thiện.

## 11_THIET_LAP_THUC_NGHIEM.md

- [Dòng 23](../chapters/11_THIET_LAP_THUC_NGHIEM.md:23) — | Revision khảo sát | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` | Mốc source, không thay hash artifact và trạng thái working tree |

- [Dòng 126](../chapters/11_THIET_LAP_THUC_NGHIEM.md:126) — | F04 | Full/delta, thêm/xóa player/entity, bỏ một update ở replica | Snapshot không bị sửa; baseline lệch được phát hiện; full phục hồi world | TV2/TV4; codec/replica assertions |

- [Dòng 130](../chapters/11_THIET_LAP_THUC_NGHIEM.md:130) — | F08 | Frame sai/cắt dở, timeout, client chậm và disconnect | Bị từ chối/cleanup theo contract; không treo vô hạn hoặc làm hỏng phòng khác | TV1/TV4; transport/writer/lifecycle test |

- [Dòng 138](../chapters/11_THIET_LAP_THUC_NGHIEM.md:138) — Reconnect resume trận không nằm trong tiêu chí nghiệm thu vì đường sản phẩm chưa bật tính năng đó;

- [Dòng 139](../chapters/11_THIET_LAP_THUC_NGHIEM.md:139) — disconnect/leave có thể kết thúc lượt ABORTED như contract hiện tại.

- [Dòng 173](../chapters/11_THIET_LAP_THUC_NGHIEM.md:173) — đồng thời kiểm tra codec, baseline, xóa entity/player và full phục hồi trước vòng đo D0.

- [Dòng 333](../chapters/11_THIET_LAP_THUC_NGHIEM.md:333) — Một run hiệu năng chỉ hợp lệ khi setup đúng roster/topology, có mẫu phù hợp, không mất baseline chưa phục hồi,

- [Dòng 340](../chapters/11_THIET_LAP_THUC_NGHIEM.md:340) — Hồ sơ nhiệm vụ 1 ghi nhận 133 JUnit test với 132 pass, 1 process smoke failure,

## 12_KET_QUA.md

- [Dòng 6](../chapters/12_KET_QUA.md:6) — `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`, không thay production code, test, luật game hoặc timeout.

- [Dòng 17](../chapters/12_KET_QUA.md:17) — | Maven offline, gọi trực tiếp sau khi được phép truy cập môi trường | 38 class, 133 test; 133 pass, 0 failure/error/skipped; BUILD SUCCESS; Maven báo 39,743 s | Tổng suite, có cả test công cụ/protocol, không phải 133 kịch bản GUI |

- [Dòng 18](../chapters/12_KET_QUA.md:18) — | Check TV2 độc lập | Exit 0; bốn nhóm check API, movement, runtime và delta đều PASS | Không cộng bốn dòng PASS vào số 133 JUnit |

- [Dòng 20](../chapters/12_KET_QUA.md:20) — | Khảo sát nhiệm vụ 1, cùng revision | 133 test, 132 pass, 1 failure; smoke đa tiến trình thất bại cả lần chạy riêng | Dữ liệu lịch sử được giữ; một lần PASS mới không chứng minh đã sửa nguyên nhân |

- [Dòng 43](../chapters/12_KET_QUA.md:43) — | SessionManagerTest | Các fixture quản lý phiên trong lớp | Quản lý session theo assertion đã khai báo | 3/3 đạt; không suy tính năng resume trận |

- [Dòng 45](../chapters/12_KET_QUA.md:45) — | LobbyLifecycleTest | Phòng bốn người, người thứ năm; quyền/ready/start; hai phòng; chat/resync; concurrent start; leave/disconnect; chơi lượt mới cùng TCP | Roster/quyền authoritative, room tách biệt, match epoch mới, quay lại phòng và cleanup | 7/7 đạt qua TCP loopback |

- [Dòng 59](../chapters/12_KET_QUA.md:59) — Chúng chưa chứng minh bốn người ở bốn máy thao tác giao diện thành công, hoặc reconnect khôi phục trận đang chơi.

- [Dòng 96](../chapters/12_KET_QUA.md:96) — | DeltaCompressionTest → DeltaCompressionCheck | Full đầu, delta tile/entity, xóa entity/player, build chưa commit, bỏ update, full phục hồi và full cũ | 1/1 JUnit đạt; check riêng PASS |

- [Dòng 105](../chapters/12_KET_QUA.md:105) — sau đó full state phục hồi được replica. Vòng trace còn đối chiếu map, số entity và vị trí x của player với nhánh full

- [Dòng 125](../chapters/12_KET_QUA.md:125) — | MatchLifecycleIntegrationTest | Kết quả cuối, replay/disconnect và trạng thái mở rộng | Final snapshot, GAME_OVER và state client theo assertion | 5/5 đạt; trùng lớp đã dẫn ở 12.2 |

- [Dòng 161](../chapters/12_KET_QUA.md:161) — | LobbyLifecycleTest | Concurrent start, replay match epoch, disconnect/host transfer và start failure | 7/7 đạt | Luồng TCP loopback đã kiểm tra, chưa phải LAN |

- [Dòng 194](../chapters/12_KET_QUA.md:194) — | LobbyLifecycleTest | 7 | 3 | 21/21 | Capacity/quyền, concurrent start, replay, disconnect và lỗi start |

- [Dòng 195](../chapters/12_KET_QUA.md:195) — | Tổng | 28 | 3 | 84/84 | Không cộng các lần lặp này vào 133 test của suite nhiệm vụ 12 |

- [Dòng 250](../chapters/12_KET_QUA.md:250) — Không có full do mất baseline, queue đầy hoặc disconnect trong phép đo này.

- [Dòng 283](../chapters/12_KET_QUA.md:283) — không được gộp thành kiểm tra mọi field v5. Đây là kiểm tra harness, không làm tăng số 133 JUnit ở 12.1.

- [Dòng 479](../chapters/12_KET_QUA.md:479) — khả năng phục hồi baseline được kiểm tra bằng fixture riêng, không phải do benchmark đã gây mất delta.

## 13_THAO_LUAN.md

- [Dòng 16](../chapters/13_THAO_LUAN.md:16) — | Phòng, quyền, movement và gameplay authoritative — FR01–FR09 | Suite 133/133 JUnit đạt ở lượt mới; test lobby/TCP, collision, bom/item/lives | Các fixture đã chạy đạt assertion; chưa nghiệm thu mọi thao tác GUI/LAN |

- [Dòng 89](../chapters/13_THAO_LUAN.md:89) — Việc chọn chu kỳ full khác có thể thay đổi byte/phục hồi, nhưng chưa có sweep tham số để gọi 100 tick là tối ưu.

- [Dòng 113](../chapters/13_THAO_LUAN.md:113) — Cách xử lý này bảo vệ một số invariant về tài nguyên và thứ tự, nhưng có thể kết thúc lượt theo ABORTED.

- [Dòng 114](../chapters/13_THAO_LUAN.md:114) — Không nên gọi đây là phục hồi trong suốt cho người chơi hoặc exactly-once toàn hệ thống.

## 14_DIEM_MOI_VA_DONG_GOP.md

- [Dòng 21](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:21) — So sánh B0/B1 đã kiểm soát chuỗi state, số tick, codec, envelope và yêu cầu phục hồi replica của harness.

- [Dòng 98](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:98) — “không lag”, “không mất kết nối” hoặc reconnect resume vào danh sách đóng góp đã chứng minh.

- [Dòng 103](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:103) — XML/log của suite 133 test và 84 lần thực thi test reliability bổ sung.

- [Dòng 119](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:119) — | C3 — Contract đồng bộ client và xử lý gián đoạn | ACK/replay, full-resync, match scope, respawn reset; giới hạn queue/deadline và cleanup khi lỗi | Controller/replica; MatchLifecycle/LobbyLifecycle, Client/TransportStability; ba lượt reliability 84/84 đạt | TV1–TV4 theo module; không tuyên bố exactly-once, reconnect resume hoặc UX đã nghiệm thu |

## 15_HAN_CHE.md

- [Dòng 3](../chapters/15_HAN_CHE.md:3) — > **Phân công: TV1 xác nhận session/room và chính sách disconnect; TV2 xác nhận đồng bộ/movement/client; TV3 xác nhận gameplay; TV4 tổng hợp phạm vi bằng chứng và công cụ đo.**

- [Dòng 10](../chapters/15_HAN_CHE.md:10) — ## 15.1. Hạn chế chức năng và reconnect

- [Dòng 12](../chapters/15_HAN_CHE.md:12) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận

- [Dòng 14](../chapters/15_HAN_CHE.md:14) — Ứng dụng hiện kết thúc lượt theo ABORTED khi người chơi disconnect/leave theo flow lobby.

- [Dòng 15](../chapters/15_HAN_CHE.md:15) — Route RECONNECT chưa được đăng ký trong ứng dụng; connect lại từ UI là một phiên mới,

- [Dòng 16](../chapters/15_HAN_CHE.md:16) — không đưa player trở lại world đang chơi. Đây là chính sách hiện hành, không phải một flow resume đã nghiệm thu.

- [Dòng 18](../chapters/15_HAN_CHE.md:18) — SessionManager có token, thời gian giữ metadata và API reconnect legacy;

- [Dòng 19](../chapters/15_HAN_CHE.md:19) — runtime cũng có command đóng băng/mở đóng băng player. Các thành phần này chưa tạo thành reconnect end-to-end.

- [Dòng 20](../chapters/15_HAN_CHE.md:20) — Khi trận đã bị dọn, chỉ gắn socket mới hoặc gửi lại full không thể phục hồi world cũ.

- [Dòng 22](../chapters/15_HAN_CHE.md:22) — [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md) và test transport/lifecycle được dẫn ở mục 12.4.

- [Dòng 45](../chapters/15_HAN_CHE.md:45) — | L01 | Chưa có resume trận; disconnect có thể ABORTED | Người chơi không tiếp tục cùng match sau mất kết nối | Lobby flow và RECONNECT_ASSESSMENT |

- [Dòng 55](../chapters/15_HAN_CHE.md:55) — Các invariant được bảo vệ trong test không đồng nghĩa delivery exactly-once hoặc phục hồi trong suốt cho mọi lỗi.

## 16_HUONG_PHAT_TRIEN.md

- [Dòng 34](../chapters/16_HUONG_PHAT_TRIEN.md:34) — | P2 | L01 | Thiết kế resume có xác thực và generation | Qua ma trận race/resume/full-baseline và luật hết hạn đã thống nhất | TV1/TV2/TV4, TV3 xác nhận gameplay |

- [Dòng 63](../chapters/16_HUONG_PHAT_TRIEN.md:63) — và kiểm tra lại MOVE/plant/disconnect cùng tick, tránh đổi ý nghĩa gameplay ngoài dự kiến.

- [Dòng 78](../chapters/16_HUONG_PHAT_TRIEN.md:78) — ## 16.3. Reconnect có xác thực/generation an toàn

- [Dòng 80](../chapters/16_HUONG_PHAT_TRIEN.md:80) — Resume là thay đổi nhiều lớp, không chỉ thêm handler RECONNECT.

- [Dòng 82](../chapters/16_HUONG_PHAT_TRIEN.md:82) — player bị đứng yên hay vẫn chịu damage, khi nào hết hạn và xử lý kết quả nếu trận kết thúc trong lúc mất kết nối.

- [Dòng 83](../chapters/16_HUONG_PHAT_TRIEN.md:83) — Chính sách này sẽ thay một phần hành vi ABORTED hiện tại nên phải được đặc tả và test cùng gameplay.

- [Dòng 85](../chapters/16_HUONG_PHAT_TRIEN.md:85) — Thiết kế phiên cần xác thực quyền nhận lại player, quy định hạn/đổi token, request lặp và reconnect đồng thời.

- [Dòng 95](../chapters/16_HUONG_PHAT_TRIEN.md:95) — **Bảng 16.2. Ma trận kiểm tra tối thiểu đề xuất cho resume.**

- [Dòng 99](../chapters/16_HUONG_PHAT_TRIEN.md:99) — | Quyền/đồng thời | Token sai/hết hạn/dùng lại; hai reconnect cùng lúc | Không chiếm ghế; chỉ owner được nhận theo policy |

- [Dòng 101](../chapters/16_HUONG_PHAT_TRIEN.md:101) — | Deadline | Trước/sau grace; reconnect khi GAME_OVER đã chốt | State/ghế/kết quả tuân theo chính sách, không hồi sinh trận đã kết thúc |

- [Dòng 104](../chapters/16_HUONG_PHAT_TRIEN.md:104) — | Cleanup | Resume lỗi giữa handshake/attach/full | Không để hai writer active, ghost player hoặc tài nguyên không có owner |

- [Dòng 106](../chapters/16_HUONG_PHAT_TRIEN.md:106) — Căn cứ phạm vi: [RECONNECT_ASSESSMENT](../../docs/RECONNECT_ASSESSMENT.md).

## 17_KET_LUAN.md

- [Dòng 22](../chapters/17_KET_LUAN.md:22) — Kiểm thử mới ghi nhận suite 133/133 JUnit đạt và 84/84 lần thực thi test reliability bổ sung đạt.

- [Dòng 31](../chapters/17_KET_LUAN.md:31) — GUI nhiều máy và profiling chưa được nghiệm thu/đo đầy đủ; resume trận chưa được triển khai trong ứng dụng;

- [Dòng 37](../chapters/17_KET_LUAN.md:37) — đánh giá tối ưu đồng bộ/correction trên trace thực, rồi mở rộng resume và tải nhiều room theo tiêu chí ở mục 16.

## 19_PHU_LUC.md

- [Dòng 38](../chapters/19_PHU_LUC.md:38) — RECONNECT có mã 0043 nhưng chưa có flow resume trong lobby.

- [Dòng 144](../chapters/19_PHU_LUC.md:144) — | [task12](../evidence/task12-2026-10-26/README.md) | 133/133 JUnit mới, check/main, XML và smoke log | Một lượt suite đầy đủ; không xóa lịch sử fail |

- [Dòng 146](../chapters/19_PHU_LUC.md:146) — | [task14](../evidence/task14-2026-10-26/README.md) | Raw CSV/log network, reliability XML, manifest/checksum và lỗi môi trường | 45 network run và 84 thực thi test bổ sung; không cộng vào 133 test |

- [Dòng 217](../chapters/19_PHU_LUC.md:217) — Đây là tóm tắt control flow, không mô tả correction smoothing hoặc resume đã triển khai.

