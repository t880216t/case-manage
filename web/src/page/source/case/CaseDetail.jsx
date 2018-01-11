import React,{Component} from 'react';
import { Table, Select,Tooltip ,Button,message,Popconfirm,Modal,Input,Icon,Upload} from 'antd';
import 'whatwg-fetch';
import Page from 'framework/page'
import {local, session} from 'common/util/storage.js'
import {hashHistory} from 'react-router'

class CaseDetail extends React.Component{
    state = {
        //初始表数据
        fetch_data:[],
        isLoading:false,
        isConfirmLoading:false,
        userID:'',
        userName:'',
        showMoreAction:false,
        showAdd:false,
        newCase:'',
        fileList: [],
        uploading: false,
        showModelTitle:'',
        projectentry:''

    }

    componentDidMount(){
        var entry = this.props.params.entry
        const userInfo = session.get('userInfo') || {userID: 0}
        this.setState({
            userID : userInfo.userID,
            userName : userInfo.userName,
            isLoading:true,
            projectentry:entry,
        },()=> {this.fetchList()})
    }

    handleUpload = () => {
        const { fileList } = this.state;
        if (fileList.length>1){
            message.warning('暂不支持多文件上传，请只保留一个')
            return
        }
        const formData = new FormData();
        fileList.forEach((file) => {
            formData.append('file', file);
            formData.append('userID', this.state.userID);
        });

        this.setState({
            uploading: true,
        });

        fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            //设置请求头，请求体为json格式，identity为未压缩
            headers: {},
            body: formData,
        }).then((response) => response.json())
            .then((responseData)=> {
                if(responseData.code === 0){
                    this.setState({
                        uploading: false,
                        fileList:[],
                    },()=>{message.success(responseData.msg)
                        this.fetchList()});
                }else {
                    this.setState({
                        uploading: false,
                    },()=>{message.error(responseData.msg)});
                }
            }).catch((error)=> {
            this.setState({
                uploading: false,
            })
            if (error.statusText){
                message.error(error.statusText)
            }else{
                message.error("网络异常，请检查您的办公网络！")
            }
        })
    }

    fetchList=()=>{
        var par = "entry="+this.state.projectentry+"&userID="+this.state.userID
        fetch('http://127.0.0.1:5000/gettaskdetail',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    this.setState({
                        fetch_data:responseData.content,
                        isLoading:false
                    })
                }
                if (responseData.code === 10001) {
                    this.setState({
                        fetch_data:[],
                        isLoading:false,

                    })
                }
            })
            .catch((error)=> {
                this.setState({
                    isLoading:false
                })
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })
    }

    //置用例状态
    setCaseStatus=(status)=>{
        var par = "entry="+this.state.showModelEntry+"&status="+status.toString()+"&updateUser="+this.state.userName
        fetch('http://127.0.0.1:5000/settaskstatus',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    message.success(responseData.msg)
                    this.setState({
                        showMoreAction:false,
                    },()=>{this.fetchList()})
                } else {
                    message.error(responseData.msg)
                }
            })
            .catch((error)=> {
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })
    }

    //更多操作
    handleMoreAction = (entry,text) =>{
        this.setState({
            showMoreAction:true,
            showModelTitle:text,
            showModelEntry:entry,
            newCase:'',
        })
    }

    //新建子用例
    handleSubmit=()=>{
        if(this.state.newCase === ''){
            message.warning('请填写用例名称')
            return
        }
        var par = "entry="+this.state.showModelEntry+"&newCase="+this.state.newCase
        fetch('http://127.0.0.1:5000/addcase',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    message.success(responseData.msg)
                    this.setState({
                        showMoreAction:false,
                        showAdd:false,
                    },()=>{this.fetchList()})
                } else {
                    message.error(responseData.msg)
                }
            })
            .catch((error)=> {
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })
    }

    //删除用例
    handleDelete=()=>{
        var par = "entry="+this.state.showModelEntry
        fetch('http://127.0.0.1:5000/deletecase',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    message.success(responseData.msg)
                    this.setState({
                        showMoreAction:false,
                    },()=>{this.fetchList()})
                } else {
                    message.error(responseData.msg)
                }
            })
            .catch((error)=> {
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })
    }

    //公开项目
    openProject=()=>{
        var par = "entry="+this.state.projectentry+"&userID="+this.state.userID
        fetch('http://127.0.0.1:5000/openproject',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    message.success('已置为公开用例')
                    this.fetchList()
                } else {
                    message.error(responseData.msg)
                }
            })
            .catch((error)=> {
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })

    }

    //重置项目状态
    initProject=()=>{
        var par = "entry="+this.state.projectentry+"&userID="+this.state.userID
        fetch('http://127.0.0.1:5000/initProjectStatus',{
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: par
        }).then((response) => {
            return response.json()}) //把response转为json
            .then((responseData) => { // 上面的转好的json
                if (responseData.code === 0) {
                    message.success('已重置用例执行状态')
                    this.fetchList()
                } else {
                    message.error(responseData.msg)
                }
            })
            .catch((error)=> {
                if (error.statusText){
                    message.error(error.statusText)
                }else{
                    message.error("网络异常，请检查您的办公网络！")
                }
            })

    }

    render(){
        const { fetch_data,uploading} = this.state;
        const props = {
            action: '//127.0.0.1:5000/upload',
            onRemove: (file) => {
                this.setState(({ fileList }) => {
                    const index = fileList.indexOf(file);
                    const newFileList = fileList.slice();
                    newFileList.splice(index, 1);
                    return {
                        fileList: newFileList,
                    };
                });
            },
            beforeUpload: (file) => {
                this.setState(({ fileList }) => ({
                    fileList: [...fileList, file],
                }));
                return false;
            },
            fileList: this.state.fileList,
        };
        const columns = [ {
            title: 'title',
            dataIndex: 'title',
            key: 'title',
            render:  (text, record) => {
                return(
                    record.status === 2?
                        record.id ===1?
                            <a style={{width:'100%',marginLeft:30,fontSize:16}}>
                                {text}
                                <span style={{marginLeft:'40%',fontSize:14,fontWeight:'bold',}}>process: {Math.round((record.doneCount / record.totalCount)*100)}%</span>
                                <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#3dbb2b'}}>pass: {record.doneCount}</span>
                                <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#ff9933'}}>fail: {record.failedCount}</span>
                                <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'rgba(0, 0, 0, 0.65)'}}>total: {record.totalCount}</span>
                            </a>
                            :
                            <Tooltip placement="top"  title={<span>最后修改人：{record.updateUser} <br/> 最后修改时间：{record.updateTime}</span>}>
                                <div style={{fontSize:16,color:'#454545'}} onClick={()=>{this.handleMoreAction(record.entry,text)}}>
                                    {text.split(' ').map((text_item)=>{
                                        return(<p key={(Math.random() * Date.now()).toFixed(0)} style={{color:'red',marginLeft:30,fontSize:16}} >{text_item}</p>)
                                    })}
                                </div>
                            </Tooltip>

                        :
                        record.status === 1?
                            record.id ===1?
                                <a style={{width:'100%',marginLeft:30,fontSize:16}} >
                                    {text}
                                    <span style={{marginLeft:'40%',fontSize:14,fontWeight:'bold',}}>process: {Math.round((record.doneCount / record.totalCount)*100)}%</span>
                                    <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#3dbb2b'}}>pass: {record.doneCount}</span>
                                    <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#ff9933'}}>fail: {record.failedCount}</span>
                                    <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'rgba(0, 0, 0, 0.65)'}}>total: {record.totalCount}</span>
                                </a>
                                :
                                <Tooltip placement="top"  title={<span>最后修改人：{record.updateUser} <br/> 最后修改时间：{record.updateTime}</span>}>
                                    <div style={{fontSize:16,color:'#454545'}} onClick={()=>{this.handleMoreAction(record.entry,text)}}>
                                        {text.split(' ').map((text_item)=>{
                                            return(<p key={(Math.random() * Date.now()).toFixed(0)} style={{color:'green',marginLeft:30,fontSize:16}} >{text_item}</p>)
                                        })}
                                    </div>
                                </Tooltip>
                            :
                            record.children.length > 0?
                                record.id ===1?
                                    <a style={{width:'100%',marginLeft:30,fontSize:16}} >
                                        {text}
                                        <span style={{marginLeft:'40%',fontSize:14,fontWeight:'bold',}}>process: {Math.round((record.doneCount / record.totalCount)*100)}%</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#3dbb2b'}}>pass: {record.doneCount}</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#ff9933'}}>fail: {record.failedCount}</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'rgba(0, 0, 0, 0.65)'}}>total: {record.totalCount}</span>
                                    </a>
                                    :
                                    <a style={{marginLeft:30,fontSize:16}} onClick={()=>{this.handleMoreAction(record.entry,text)}}>{text}</a>
                                :
                                record.id ===1?
                                    <a style={{width:'100%',marginLeft:30,fontSize:16}}>
                                        {text}
                                        <span style={{marginLeft:'40%',fontSize:14,fontWeight:'bold',}}>process: {Math.round((record.doneCount / record.totalCount)*100)}%</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#3dbb2b'}}>pass: {record.doneCount}</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#ff9933'}}>fail: {record.failedCount}</span>
                                        <span style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'rgba(0, 0, 0, 0.65)'}}>total: {record.totalCount}</span>
                                    </a>
                                    :
                                    <div style={{fontSize:16,color:'#454545'}} onClick={()=>{this.handleMoreAction(record.entry,text)}}>
                                        {text.split(' ').map((text_item)=>{
                                            return(<p key={(Math.random() * Date.now()).toFixed(0)}>{text_item}</p>)
                                        })}
                                    </div>
                )}
        }];

        return(
            <Page title="case详情" loading={this.state.isLoading}>
                <div style={{display:'flex',flexDirection:'row',justifyContent:'flex-end',marginBottom:20,marginTop:20,marginRight:40}}>

                    {fetch_data.length>0?
                        fetch_data[0].order_user === 0?
                        <div>
                            <span>当前为公开用例，所有用户可见。</span>
                            <Button style={{marginLeft:10,fontSize:14,fontWeight:'bold'}} onClick={()=>{message.warning('如需置为私有，请联系管理员。')}}>公开</Button>
                            <Popconfirm title="你确定要重置这个项目的执行状态吗?" onConfirm={()=>{this.initProject()}} okText="确定" cancelText="取消">
                                <Button style={{marginLeft:10,fontSize:14,fontWeight:'bold', backgroundColor: 'red',color:'white'}}>重置状态</Button>
                            </Popconfirm>
                        </div>

                        :
                        <div>
                            <span>当前为私有用例，只有你可见。</span>
                            <Popconfirm title="你确定要公开这个项目吗?" onConfirm={()=>{this.openProject()}} okText="确定" cancelText="取消">
                                <Button style={{marginLeft:10,fontSize:14,fontWeight:'bold',color:'#108ee9'}}>我要公开</Button>
                            </Popconfirm>
                            <Popconfirm title="你确定要重置这个项目的执行状态吗?" onConfirm={()=>{this.initProject()}} okText="确定" cancelText="取消">
                                <Button style={{marginLeft:10,fontSize:14,fontWeight:'bold', backgroundColor: 'red',color:'white'}}>重置状态</Button>
                            </Popconfirm>
                        </div>
                    :
                        <div></div>

                    }
                </div>

                <Table rowKey="entry" columns={columns} dataSource={fetch_data} indentSize={50} scroll={{ x: '130%', y: 1000 }} defaultExpandAllRows={true} />
                <Modal title={this.state.showModelTitle!=''?
                    this.state.showModelTitle.split(' ').map((text_item)=>{
                        return(<p key={(Math.random() * Date.now()).toFixed(0)}>{text_item}</p>)
                    }):
                    this.state.showModelTitle
                }
                       visible={this.state.showMoreAction}
                       onOk={()=>{console.log('handle ok')}}
                       onCancel={()=>{this.setState({showMoreAction:false,showAdd:false})}}
                       footer={null}
                >
                    {this.state.showAdd?
                        <div style={{display:"flex",flexDirection:'row', marginTop:20,marginBottom:30}}>
                            <Input value={this.state.newCase} onChange = {(value)=>{this.setState({newCase:value.target.value},()=>{console.log('newCase :',this.state.newCase)})}}
                                   placeholder="新建当前case的子用例"
                                   autosize={true}
                                   autoFocus={true}
                                   onPressEnter={()=>{this.handleSubmit()}}
                            />
                            <Button style={{backgroundColor:"#108ee9",marginLeft:10}} onClick={()=>{this.handleSubmit()}}>
                                提交
                            </Button>
                        </div>
                        :
                        <div style={{display:"flex",flexDirection:'row',justifyContent:"space-around"}}>
                            <Tooltip placement="bottomRight" title={"新建子用例"}>
                                <Icon type="plus-circle" style={{ fontSize: 40, color: '#c2c5cc' }} onClick={()=>{this.setState({showAdd:true,})}}/>
                            </Tooltip>
                            <Popconfirm title="你确定要删除该用例?" onConfirm={()=>{this.handleDelete()}} okText="确定" cancelText="取消">
                                <Tooltip placement="bottomRight" title={"删除用例"}>
                                    <Icon type="minus-circle" style={{ fontSize: 40, color: '#cc0227' }} />
                                </Tooltip>
                            </Popconfirm>
                            <Tooltip placement="bottomRight" title={"用例测试失败"}>
                                <Icon type="close-circle" style={{ fontSize: 40, color: '#ff9933' }} onClick={()=>{this.setCaseStatus(2)}}/>
                            </Tooltip>
                            <Tooltip placement="bottomRight" title={"用例测试通过"}>
                                <Icon type="check-circle" style={{ fontSize: 40, color: '#3dbb2b' }} onClick={()=>{this.setCaseStatus(1)}}/>
                            </Tooltip>
                        </div>
                    }

                </Modal>
            </Page>
        );
    }
}

export default CaseDetail;
