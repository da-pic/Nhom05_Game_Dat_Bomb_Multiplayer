package com.bombit.common.dto;

public record PlantRequestResult(int playerId,long requestId,BombType bombType,boolean accepted,String errorCode,Integer bombId) {
    public PlantRequestResult{if(playerId<=0||requestId<=0||bombType==null||accepted&&(errorCode!=null||bombId==null||bombId<=0)||!accepted&&(errorCode==null||bombId!=null))throw new IllegalArgumentException("Invalid plant result");}
}
