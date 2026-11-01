import com.bombit.client.app.GameClientConnection;
import com.bombit.client.lobby.LobbyWindow;
import com.bombit.client.ui.component.ModeSelectionPanel;
import com.bombit.client.ui.game.MovementGameWindow;
import com.bombit.common.dto.GameMode;
import com.bombit.common.protocol.JsonV3;
import com.bombit.server.app.LobbyGameServer;
import java.awt.*;
import java.awt.event.*;
import java.lang.reflect.Field;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicReference;
import javax.imageio.ImageIO;
import javax.swing.*;

/** Smoke tự động với cửa sổ thật: ActionListener lobby, Robot cho phím gameplay.
 * Không thay thế playtest của người dùng hoặc nghiệm thu nhiều máy/LAN. */
public final class Nv06GuiSmoke {
    static final ArrayList<String> checks=new ArrayList<>();
    static final ArrayList<String> screenshots=new ArrayList<>();
    static final java.util.List<String> edtErrors=Collections.synchronizedList(new ArrayList<>());
    static Path out;
    static <T> T edt(Callable<T> action)throws Exception {
        if(SwingUtilities.isEventDispatchThread())return action.call();
        var value=new AtomicReference<T>();var error=new AtomicReference<Throwable>();
        SwingUtilities.invokeAndWait(()->{try{value.set(action.call());}catch(Throwable e){error.set(e);}});
        if(error.get()!=null)throw new Exception(error.get());return value.get();
    }
    static Object field(Object target,String name)throws Exception{Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(target);}
    static GameClientConnection client(LobbyWindow w)throws Exception{return (GameClientConnection)field(w,"client");}
    static MovementGameWindow game(LobbyWindow w)throws Exception{return (MovementGameWindow)field(w,"game");}
    static void click(LobbyWindow w,String name)throws Exception{edt(()->{var b=(JButton)field(w,name);if(!b.isEnabled())throw new AssertionError(name+" disabled");b.doClick();return null;});}
    static void until(String label,Callable<Boolean> condition)throws Exception{
        long end=System.nanoTime()+8_000_000_000L;
        while(System.nanoTime()<end){if(edt(condition)){checks.add(label);System.out.println("PASS: "+label);return;}Thread.sleep(50);}
        throw new AssertionError("Timeout: "+label);
    }
    static void shot(Window window,String name)throws Exception{
        edt(()->{window.setLocation(0,0);window.toFront();window.requestFocus();return null;});
        Thread.sleep(250);
        Rectangle area=edt(window::getBounds).intersection(new Rectangle(Toolkit.getDefaultToolkit().getScreenSize()));
        ImageIO.write(new Robot().createScreenCapture(area),"png",out.resolve(name+".png").toFile());screenshots.add(name+".png");
    }
    static JButton replay(Component root){
        if(root instanceof JButton b&&b.getText().contains("CHƠI LẠI"))return b;
        if(root instanceof Container c)for(var child:c.getComponents()){var b=replay(child);if(b!=null)return b;}return null;
    }
    public static void main(String[] args)throws Exception{
        out=Path.of(args[0]).toAbsolutePath();Files.createDirectories(out);
        if(Files.exists(out.resolve("gui-summary.json")))throw new IllegalStateException("Keep completed GUI run immutable");
        long start=System.nanoTime();LobbyGameServer server=null;Thread accept=null;LobbyWindow a=null,b=null;Throwable failure=null;
        var facts=new LinkedHashMap<String,Object>();
        try{
            if(GraphicsEnvironment.isHeadless())throw new IllegalStateException("Desktop unavailable");
            Toolkit.getDefaultToolkit().getSystemEventQueue().push(new EventQueue(){@Override protected void dispatchEvent(AWTEvent event){try{super.dispatchEvent(event);}catch(Throwable t){edtErrors.add(t.toString());t.printStackTrace();}}});
            server=new LobbyGameServer(0);var owner=server;accept=new Thread(()->{try{owner.start();}catch(Exception e){edtErrors.add(e.toString());}},"NV06-GUI-Server");accept.start();
            int port=server.port();facts.put("host","127.0.0.1");facts.put("port",port);facts.put("protocol",3);facts.put("snapshot",6);
            a=edt(()->new LobbyWindow("127.0.0.1",port,"NV06 GUI A"));b=edt(()->new LobbyWindow("127.0.0.1",port,"NV06 GUI B"));
            var host=a;var guest=b;edt(()->{host.setVisible(true);guest.setVisible(true);return null;});
            click(a,"connect");click(b,"connect");
            until("Two GUI clients connected to strict v3 lobby",()->client(host)!=null&&client(guest)!=null&&client(host).sessionId()!=null&&client(guest).sessionId()!=null&&((JButton)field(host,"create")).isEnabled());
            until("Server mode descriptors visible",()->((ModeSelectionPanel)field(host,"createMode")).selector().getItemCount()==4);
            edt(()->{var selector=(ModeSelectionPanel)field(host,"createMode");selector.selector().setSelectedItem(GameMode.SHADOW_RELAY);if(selector.selectedMode()!=GameMode.CLASSIC)throw new AssertionError("Unavailable mode selected");return null;});
            checks.add("Unavailable Shadow cannot replace Classic selection");shot(a,"01-mode-browser");
            click(a,"create");until("Create Classic room",()->client(host).roomState()!=null);
            until("Guest room list populated",()->((JTable)field(guest,"roomTable")).getRowCount()==1);
            edt(()->{((JTable)field(guest,"roomTable")).setRowSelectionInterval(0,0);return null;});click(b,"join");
            until("Join same Classic configuration",()->client(guest).roomState()!=null&&client(host).roomState().players().size()==2);
            var config=edt(()->client(host).roomState().configuration().configurationId());facts.put("configurationId",config.toString());
            shot(a,"02-classic-room");click(b,"ready");until("Host start enabled by current READY revision",()->((JButton)field(host,"start")).isEnabled());click(a,"start");
            until("Both game windows receive v6 full and unlock input",()->game(host)!=null&&game(guest)!=null&&client(host).movement().isInputReady()&&client(guest).movement().isInputReady());
            var match=edt(()->client(host).context().matchId());facts.put("matchId",match.toString());
            shot(game(a),"03-classic-arena");
            double x=edt(()->client(host).movement().world().getPlayers().get(client(host).localId()).getX());
            // Chỉ Robot gửi phím; phần lobby gọi đúng ActionListener của các nút đang hiển thị.
            edt(()->{game(host).toFront();game(host).requestFocus();game(host).getRootPane().requestFocusInWindow();return null;});Thread.sleep(200);
            var robot=new Robot();robot.keyPress(KeyEvent.VK_RIGHT);Thread.sleep(250);robot.keyRelease(KeyEvent.VK_RIGHT);
            until("Physical arrow key changes authoritative position",()->client(host).movement().world().getPlayers().get(client(host).localId()).getX()>x+1);
            robot.keyPress(KeyEvent.VK_SPACE);Thread.sleep(70);robot.keyRelease(KeyEvent.VK_SPACE);
            until("Physical Space receives authoritative PLANT_RESULT",()->client(host).lastPlantResult()!=null);
            facts.put("plantResult",edt(()->client(host).lastPlantResult().getJsonPayload()));
            long epoch=edt(()->client(host).metadata().stream().viewEpoch());
            long tick=edt(()->client(host).movement().world().getTick());
            String session=edt(()->client(host).sessionId());
            var movement=edt(()->client(host).movement());server.transport().getSessionManager().find(session).orElseThrow().closeSocket();
            until("Reconnect keeps controller, receives fresh full, unlocks input",()->client(host).metadata().stream().viewEpoch()>epoch&&!client(host).isReconnecting()&&client(host).movement()==movement&&movement.isInputReady()&&movement.world().getTick()>tick);
            facts.put("recoveredViewEpoch",edt(()->client(host).metadata().stream().viewEpoch()));shot(game(a),"04-recovered-arena");
            // END dùng nút lobby thật; không đóng game window để tránh lẫn với LEAVE.
            click(a,"end");until("Both GUIs display authoritative results",()->Boolean.TRUE.equals(field(host,"showingResults"))&&Boolean.TRUE.equals(field(guest,"showingResults")));shot(a,"05-results");
            edt(()->{replay(host).doClick();replay(guest).doClick();return null;});click(b,"ready");until("Replay ready at same configuration",()->((JButton)field(host,"start")).isEnabled());click(a,"start");
            until("Replay creates new match and v6 replica",()->game(host)!=null&&game(guest)!=null&&client(host).movement().isInputReady()&&client(guest).movement().isInputReady()&&!client(host).context().matchId().equals(match));
            if(!edt(()->client(host).metadata().configuration().configurationId().equals(config)))throw new AssertionError("Room configuration changed on replay");
            checks.add("Replay retains room configurationId");facts.put("replayMatchId",edt(()->client(host).context().matchId().toString()));
            if(server.failure().isPresent())throw new AssertionError(server.failure().get());
            if(!edtErrors.isEmpty())throw new AssertionError(edtErrors.toString());
        }catch(Throwable e){failure=e;e.printStackTrace();}
        finally{
            var first=a;var second=b;
            edt(()->{for(var w:new LobbyWindow[]{first,second})if(w!=null){try{var g=game(w);if(g!=null)g.disposeGame();var c=client(w);if(c!=null)c.close();((javax.swing.Timer)field(w,"notificationTimer")).stop();w.dispose();}catch(Exception e){edtErrors.add(e.toString());}}return null;});
            if(server!=null)server.close();if(accept!=null)accept.join(3000);
            facts.put("elapsedSeconds",(System.nanoTime()-start)/1e9);facts.put("checks",checks);facts.put("screenshots",screenshots);facts.put("edtErrors",java.util.List.copyOf(edtErrors));
            boolean cleanup=edt(()->Arrays.stream(Window.getWindows()).noneMatch(Window::isDisplayable))&&(accept==null||!accept.isAlive())&&(server==null||server.snapshotWorkerCount()==0);
            facts.put("cleanup",cleanup);facts.put("status",failure==null&&cleanup&&edtErrors.isEmpty()?"PASS":"FAIL");facts.put("failure",failure==null?null:failure.toString());
            Files.writeString(out.resolve("gui-summary.json"),JsonV3.encode(facts));
        }
        System.exit(failure==null&&Boolean.TRUE.equals(facts.get("cleanup"))&&edtErrors.isEmpty()?0:1);
    }
}
